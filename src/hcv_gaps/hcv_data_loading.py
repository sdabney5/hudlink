"""
This module contains functions for loading required datasets.
Each function performs checks.

Functions:

1. load_ipums_data(filepath):
    - Loads IPUMS data from a CSV and checks for required columns and missing values.

2. load_crosswalk_data(filepath):
    - Loads MCDC crosswalk data from a CSV and performs checks.

3. load_income_limits(filepath):
    - Loads income limits data from a CSV and checks for the HUD API naming convention.

4. load_incarceration_df(filepath):
    - Loads and validates the incarceration dataset from a CSV; checks for required columns and missing values.

5. load_hud_hcv_data(filepath):
    - Loads HUD Picture of Subsidized Housing data from a CSV and checks for required columns and missing values.

Usage:
To use, import this module and call the loading functions with the correct file paths.

Example:
    import hcv_data_loading as hcv_data

    ipums_df = hcv_data.load_ipums_data('path_to_ipums_data.csv')
    crosswalk_df = hcv_data.load_crosswalk_data('path_to_crosswalk_data.csv')
    income_limits_df = hcv_data.load_income_limits('path_to_income_limits.csv')
    incarceration_df = hcv_data.load_incarceration_df('path_to_incarceration_data.csv')
    hud_hcv_df = hcv_data.load_hud_hcv_data('path_to_hud_hcv_data.csv')
"""

#imports
import pandas as pd
import logging

logging.info("This is a log message from hcv_data_loading.py")


def load_ipums_data(filepath):
    """
    Load IPUMS data from a CSV file and perform variable checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded IPUMS data (if all checks pass).

    Raises:
    ValueError: If issues are found.
    """
    try:
        # Load the dataset
        ipums_df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error loading IPUMS file: {e}")

    # Check for required columns
    required_columns = ['PUMA', 'COUNTYICP', 'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'HHWT',
                        'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER', 'NFAMS', 'FAMUNIT', 'CBSERIAL']
    missing_columns = [col for col in required_columns if col not in ipums_df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}. "
                         "Make sure the IPUMS dataset includes all necessary variables.")

    # Check for missing values
    missing_pumas = ipums_df['PUMA'].isnull().sum()
    missing_countyicp = ipums_df['COUNTYICP'].isnull().sum()
    missing_income_columns = {col: ipums_df[col].isnull().sum() for col in required_columns if ipums_df[col].isnull().sum() > 0}

    if missing_pumas > 0 or missing_countyicp > 0 or missing_income_columns:
        error_message = [f"Number of rows with missing PUMA values: {missing_pumas}",
                         f"Number of rows with missing COUNTYICP values: {missing_countyicp}"]
        for col, count in missing_income_columns.items():
            error_message.append(f"Number of rows with missing {col} values: {count}")
        raise ValueError(" | ".join(error_message) + ". Ensure there are no missing values in columns.")

    # Convert columns to appropriate types and clean string fields
    try:
        # Convert PUMA and COUNTYICP to strings and strip whitespace
        ipums_df['PUMA'] = ipums_df['PUMA'].astype(str).str.strip()
        ipums_df['COUNTYICP'] = ipums_df['COUNTYICP'].astype(str).str.strip()
        ipums_df['HHWT'] = ipums_df['HHWT'].astype(float)
        income_columns = ['HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER']
        ipums_df[income_columns] = ipums_df[income_columns].apply(pd.to_numeric, errors='coerce')
    except ValueError as e:
        raise ValueError(f"Error converting columns to appropriate types: {e}")

    logging.info("IPUMS data loaded successfully and all checks passed.")
    return ipums_df


def load_crosswalk_data(filepath_2012, filepath_2022):
    """
    Load, clean, and normalize the 2012 and 2022 MCDC crosswalk datasets.

    Parameters:
    filepath_2012 (str): Path to the 2012 crosswalk CSV file.
    filepath_2022 (str): Path to the 2022 crosswalk CSV file.

    Returns:
    tuple: Two cleaned and normalized DataFrames (crosswalk_2012_df, crosswalk_2022_df).

    Raises:
    ValueError: If the files have missing required columns, missing values, or invalid data types.
    """
    try:
        # Load the datasets
        crosswalk_2012_df = pd.read_csv(filepath_2012)
        crosswalk_2022_df = pd.read_csv(filepath_2022)

        # Define required columns
        required_columns = ['State code', 'PUMA', 'County code', 'State abbr.', 'County_Name', 'allocation factor']

        # Validate 2012 dataset
        missing_columns_2012 = [col for col in required_columns if col not in crosswalk_2012_df.columns]
        if missing_columns_2012:
            raise ValueError(f"2012 crosswalk dataset is missing required columns: {missing_columns_2012}")
        if crosswalk_2012_df.isnull().any().any():
            missing_details_2012 = crosswalk_2012_df.isnull().sum()
            raise ValueError(f"2012 crosswalk dataset contains missing values:\n{missing_details_2012}")

        # Validate 2022 dataset
        missing_columns_2022 = [col for col in required_columns if col not in crosswalk_2022_df.columns]
        if missing_columns_2022:
            raise ValueError(f"2022 crosswalk dataset is missing required columns: {missing_columns_2022}")
        if crosswalk_2022_df.isnull().any().any():
            missing_details_2022 = crosswalk_2022_df.isnull().sum()
            raise ValueError(f"2022 crosswalk dataset contains missing values:\n{missing_details_2022}")

        # Convert columns to appropriate types and clean the PUMA field for 2012 dataset
        crosswalk_2012_df['PUMA'] = crosswalk_2012_df['PUMA'].astype(str).str.strip().str.lstrip('0')
        crosswalk_2012_df['allocation factor'] = crosswalk_2012_df['allocation factor'].astype(float)

        # Convert columns to appropriate types and clean the PUMA field for 2022 dataset
        crosswalk_2022_df['PUMA'] = crosswalk_2022_df['PUMA'].astype(str).str.strip().str.lstrip('0')
        crosswalk_2022_df['allocation factor'] = crosswalk_2022_df['allocation factor'].astype(float)

        # **STEP 1: Drop Duplicate Rows on (PUMA + County_Name)**
        crosswalk_2012_df = crosswalk_2012_df.drop_duplicates(subset=['PUMA', 'County_Name'])
        crosswalk_2022_df = crosswalk_2022_df.drop_duplicates(subset=['PUMA', 'County_Name'])

        # **STEP 2: Normalize Allocation Factors (so they sum to 1 within each PUMA)**
        crosswalk_2012_df['allocation factor'] /= crosswalk_2012_df.groupby('PUMA')['allocation factor'].transform('sum')
        crosswalk_2022_df['allocation factor'] /= crosswalk_2022_df.groupby('PUMA')['allocation factor'].transform('sum')

        # New Validation: Check if allocation factors sum to 1 per PUMA
        sum_check_2012 = crosswalk_2012_df.groupby('PUMA')['allocation factor'].sum().round(6)
        sum_check_2022 = crosswalk_2022_df.groupby('PUMA')['allocation factor'].sum().round(6)

        # Find any PUMAs that are still not summing to 1
        incorrect_2012 = sum_check_2012[sum_check_2012 != 1]
        incorrect_2022 = sum_check_2022[sum_check_2022 != 1]

        if not incorrect_2012.empty:
            raise ValueError(f"2012 Crosswalk Error: Some PUMAs do not sum to 1 after normalization:\n{incorrect_2012}")

        if not incorrect_2022.empty:
            raise ValueError(f"2022 Crosswalk Error: Some PUMAs do not sum to 1 after normalization:\n{incorrect_2022}")

        logging.info("Both 2012 and 2022 crosswalk datasets loaded, cleaned, and normalized successfully.")
        return crosswalk_2012_df, crosswalk_2022_df

    except Exception as e:
        raise ValueError(f"Error loading crosswalk data: {e}")


def load_income_limits(filepath):
    """
    Load income limits data from a CSV file and perform validation checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded and validated income limits data.

    Raises:
    ValueError: If required columns are missing, data contains missing values, or invalid data types are found.
    """
    try:
        # Load the dataset
        income_limits_df = pd.read_csv(filepath)

        # Define required columns
        required_columns = ['County_Name'] + [f'il{threshold}_p{size}' for threshold in [30, 50, 80] for size in range(1, 9)]

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in income_limits_df.columns]
        if missing_columns:
            raise ValueError(f"Income limits data is missing required columns: {missing_columns}")

        # Check for missing values
        missing_county_names = income_limits_df['County_Name'].isnull().sum()
        if missing_county_names > 0:
            raise ValueError(f"Income limits data contains {missing_county_names} rows with missing 'County_Name' values.")

        missing_values_summary = {
            col: income_limits_df[col].isnull().sum()
            for col in required_columns
            if income_limits_df[col].isnull().sum() > 0
        }
        if missing_values_summary:
            missing_info = "\n".join([f"{col}: {count} missing values" for col, count in missing_values_summary.items()])
            raise ValueError(f"Income limits data contains missing values in the following columns:\n{missing_info}")

        # Convert columns to numeric
        income_limit_columns = [f'il{threshold}_p{size}' for threshold in [30, 50, 80] for size in range(1, 9)]
        income_limits_df[income_limit_columns] = income_limits_df[income_limit_columns].apply(pd.to_numeric, errors='coerce')

        # Re-check for any non-numeric values
        invalid_values = income_limits_df[income_limit_columns].isnull().sum()
        if invalid_values.sum() > 0:
            invalid_columns = [col for col in income_limit_columns if income_limits_df[col].isnull().sum() > 0]
            raise ValueError(f"Income limits data contains invalid or non-numeric values in the following columns: {', '.join(invalid_columns)}")

    except Exception as e:
        raise ValueError(f"Error loading or validating income limits data from {filepath}: {e}")

    logging.info("Income limits data loaded successfully and all checks passed.")
    return income_limits_df

def load_incarceration_df(filepath=None):
    """
    Load incarceration data from a CSV file and validate its structure.

    Parameters:
    filepath (str or None): Path to the incarceration CSV file. If None, function exits gracefully.

    Returns:
    pd.DataFrame or None: Loaded and validated incarceration data, or None if no file is provided.
    """
    if filepath is None:
        logging.info("No incarceration data provided.")
        return None

    try:
        incarceration_df = pd.read_csv(filepath)
    except Exception as e:
        logging.info(f"Error loading file: {e}")
        return None

    required_columns = ['County_Name', 'Ttl_Incarc']
    race_columns = ['Ttl_Minority_Incarc', 'Ttl_White_Incarc']

    # Check for required columns
    missing_required_columns = [col for col in required_columns if col not in incarceration_df.columns]
    if missing_required_columns:
        logging.info(f"Missing required columns: {', '.join(missing_required_columns)}. Please ensure the file has these columns.")
        return None

    missing_race_columns = [col for col in race_columns if col not in incarceration_df.columns]
    if missing_race_columns:
        logging.info(f"Attention: Missing columns {', '.join(missing_race_columns)}. Race sampling will not be available.")

    # Convert numeric columns, handling errors and missing values
    for col in required_columns + race_columns:
        if col in incarceration_df.columns:
            incarceration_df[col] = pd.to_numeric(incarceration_df[col], errors='coerce').fillna(0).astype(int)

    logging.info("Incarceration data loaded successfully.")
    return incarceration_df

def load_hud_hcv_data(filepath):
    """
    Load and validate HUD Picture of Subsidized Housing data from a CSV file.

    Parameters:
    ----------
    filepath : str
        Path to the HUD HCV data CSV file.

    Returns:
    -------
    pd.DataFrame
        Loaded and validated HUD HCV data.

    Raises:
    -------
    ValueError: If the file is missing required columns, contains missing values, or has invalid data types.

    Notes:
    ------
    - Required columns: 'Name', 'Subsidized units available', '% Minority', '%White Non-Hispanic'
    """
    try:
        # Load the dataset
        hud_hcv_df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error loading HUD HCV data from {filepath}: {e}")

    # Define required columns
    required_columns = ['Name', 'Subsidized units available', '% Minority', '%White Non-Hispanic']

    # Check for required columns
    missing_columns = [col for col in required_columns if col not in hud_hcv_df.columns]
    if missing_columns:
        raise ValueError(f"HUD HCV data is missing required columns: {', '.join(missing_columns)}. Ensure the file includes these columns.")

    # Check for missing values in required columns
    for col in required_columns:
        missing_values = hud_hcv_df[col].isnull().sum()
        if missing_values > 0:
            raise ValueError(f"HUD HCV data contains {missing_values} missing values in the '{col}' column. Please address these issues.")

    # Validate numerical columns
    try:
        hud_hcv_df['Subsidized units available'] = pd.to_numeric(hud_hcv_df['Subsidized units available'], errors='coerce')
        hud_hcv_df['% Minority'] = pd.to_numeric(hud_hcv_df['% Minority'], errors='coerce')
        hud_hcv_df['%White Non-Hispanic'] = pd.to_numeric(hud_hcv_df['%White Non-Hispanic'], errors='coerce')

        # Check for any resulting NaN values after conversion
        if hud_hcv_df[['Subsidized units available', '% Minority', '%White Non-Hispanic']].isnull().any().any():
            raise ValueError("HUD HCV data contains invalid values in numerical columns ('Subsidized units available', '% Minority', '%White Non-Hispanic').")
    except ValueError as e:
        raise ValueError(f"Error validating numerical data types in HUD HCV dataset: {e}")

    logging.info("HUD HCV data loaded successfully and all checks passed.")
    return hud_hcv_df
