"""
This module contains functions for loading various datasets required for Housing Choice Voucher (HCV) analysis.
Each function performs necessary checks to ensure the data is correctly loaded and contains all required columns.

Functions:

1. load_ipums_data(filepath):
    - Loads IPUMS data from a CSV file and checks for required columns and missing values.

2. load_crosswalk_data(filepath):
    - Loads MCDC crosswalk data from a CSV file and performs checks to ensure data integrity.

3. load_income_limits(filepath):
    - Loads income limits data from a CSV file and ensures it follows the HUD API naming convention.

4. load_incarceration_df(file_path=None):
    - Loads and validates the incarceration dataset, checking for required columns and missing values.

5. load_hud_hcv_data(filepath):
    - Loads HUD Picture of Subsidized Housing data from a CSV file and checks for required columns and missing values.

Usage:
To use, import this module and call the desired data loading functions with the appropriate file paths.

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

def load_ipums_data(filepath):
    """
    Load IPUMS data from a CSV file and perform variable checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded IPUMS data (if all checks pass).

    Notes:
    - Ensure the IPUMS dataset includes the columns 'PUMA', 'COUNTYICP', and all relevant income-related columns ( see required_columns).
    - Verify that the 'PUMA' column contains values that can be converted to integers.
    """
    try:
        # Load the dataset
        ipums_df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Check for required columns
    required_columns = ['PUMA', 'COUNTYICP', 'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER', 'NFAMS', 'FAMUNIT', 'CBSERIAL']
    missing_columns = [col for col in required_columns if col not in ipums_df.columns]
    if missing_columns:
        print(f"Missing required columns: {', '.join(missing_columns)}")
        print("Ensure the IPUMS dataset includes columns named 'PUMA', 'COUNTYICP', and relevant income-related columns.")
        return None

    # Check for missing values
    missing_pumas = ipums_df['PUMA'].isnull().sum()
    missing_countyicp = ipums_df['COUNTYICP'].isnull().sum()
    missing_income_columns = {col: ipums_df[col].isnull().sum() for col in required_columns if ipums_df[col].isnull().sum() > 0}

    if missing_pumas > 0 or missing_countyicp > 0 or missing_income_columns:
        print(f"Number of rows with missing PUMA values: {missing_pumas}")
        print(f"Number of rows with missing COUNTYICP values: {missing_countyicp}")
        for col, count in missing_income_columns.items():
            print(f"Number of rows with missing {col} values: {count}")
        print("Ensure there are no missing values in the 'PUMA', 'COUNTYICP', and relevant income-related columns.")
        return None

    # Convert columns to appropriate types
    try:
        ipums_df['PUMA'] = ipums_df['PUMA'].astype(str)
        ipums_df['COUNTYICP'] = ipums_df['COUNTYICP'].astype(str)
        ipums_df['HHWT'] = ipums_df['HHWT'].astype(float)
        income_columns = ['HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER']
        ipums_df[income_columns] = ipums_df[income_columns].apply(pd.to_numeric, errors='coerce')
    except ValueError as e:
        print(f"Error converting columns to appropriate types: {e}")
        return None

    print("IPUMS data loaded successfully and all checks passed.")
    return ipums_df

import pandas as pd



def load_crosswalk_data(filepath):
    """
    Load MCDC crosswalk data from a CSV file and perform checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded crosswalk data if all checks pass.
    """
    try:
        # Load the dataset
        crosswalk_df = pd.read_csv(filepath)

        # Remove the first row and set the second row as the header
        crosswalk_df.columns = crosswalk_df.iloc[0]
        crosswalk_df = crosswalk_df[1:].reset_index(drop=True)

        # Rename columns for consistency
        if 'PUMA (2022)' in crosswalk_df.columns:
            crosswalk_df = crosswalk_df.rename(columns={
                'PUMA (2022)': 'PUMA',
                'PUMA22 name': 'PUMA_Name',
                'puma22-to-county allocation factor': 'allocation_factor'
            })
        elif 'PUMA (2012)' in crosswalk_df.columns:
            crosswalk_df = crosswalk_df.rename(columns={
                'PUMA (2012)': 'PUMA',
                'PUMA12 name': 'PUMA_Name',
                'puma12 to county allocation factor': 'allocation_factor'
            })

    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Define the required columns for each version
    required_columns = ['PUMA', 'County name', 'PUMA_Name', 'County code', 'allocation_factor']

    # Check for required columns
    if not all(col in crosswalk_df.columns for col in required_columns):
        print("Missing required columns. Ensure the crosswalk dataset includes the correct columns.")
        return None

def load_crosswalk_data(filepath):
    """
    Load MCDC crosswalk data from a CSV file and perform checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded crosswalk data if all checks pass.
    """
    try:
        # Load the dataset
        crosswalk_df = pd.read_csv(filepath)

        # Remove the first row and set the second row as the header
        crosswalk_df.columns = crosswalk_df.iloc[0]
        crosswalk_df = crosswalk_df[1:].reset_index(drop=True)

        # Rename columns for consistency
        if 'PUMA (2022)' in crosswalk_df.columns:
            crosswalk_df = crosswalk_df.rename(columns={
                'PUMA (2022)': 'PUMA',
                'PUMA22 name': 'PUMA_Name',
                'puma22-to-county allocation factor': 'allocation_factor'
            })
        elif 'PUMA (2012)' in crosswalk_df.columns:
            crosswalk_df = crosswalk_df.rename(columns={
                'PUMA (2012)': 'PUMA',
                'PUMA12 name': 'PUMA_Name',
                'puma12-to-county allocation factor': 'allocation_factor'
            })

    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Define the required columns for each version
    required_columns = ['PUMA', 'County name', 'PUMA_Name', 'County code', 'allocation_factor']

    # Check for required columns
    if not all(col in crosswalk_df.columns for col in required_columns):
        print("Missing required columns. Ensure the crosswalk dataset includes the correct columns.")
        return None

    # Check for missing values
    missing_pumas = crosswalk_df['PUMA'].isnull().sum()
    missing_county_names = crosswalk_df['County name'].isnull().sum()
    if missing_pumas > 0 or missing_county_names > 0:
        print(f"Number of rows with missing PUMA values: {missing_pumas}")
        print(f"Number of rows with missing County name values: {missing_county_names}")
        print("Ensure there are no missing values in the 'PUMA' or 'County name' columns.")
        return None

    # Convert columns to appropriate types
    try:
        crosswalk_df['PUMA'] = crosswalk_df['PUMA'].astype(str).str.lstrip('0')  # Remove leading zeros
        crosswalk_df['County code'] = crosswalk_df['County code'].astype(str)
        crosswalk_df['allocation_factor'] = crosswalk_df['allocation_factor'].astype(float)
    except ValueError as e:
        print(f"Error converting columns to appropriate types: {e}")
        return None

    print("Crosswalk data loaded successfully and all checks passed.")
    return crosswalk_df



def load_income_limits(filepath):
    """
    Load income limits data from a CSV file and perform checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded income limits data if all checks pass.

    Notes:
    - Ensure the income limits dataset follows the HUD API naming convention (e.g., 'il50_p1', 'il30_p1', 'il80_p1').
    - Ensure that the `County_Name` column values match the format used in the IPUMS dataset (e.g., 'Alachua FL').
    """
    try:
        # Load the dataset
        income_limits_df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Check for required columns
    required_columns = ['County_Name'] + [f'il{threshold}_p{size}' for threshold in [30, 50, 80] for size in range(1, 9)]
    missing_columns = [col for col in required_columns if col not in income_limits_df.columns]
    if missing_columns:
        print(f"Missing required columns: {', '.join(missing_columns)}")
        print("Ensure the income limits dataset includes the County_Name column and follows the HUD API naming convention for income limit columns.")
        return None

    # Check for missing values
    missing_county_names = income_limits_df['County_Name'].isnull().sum()
    if missing_county_names > 0:
        print(f"Number of rows with missing County_Name values: {missing_county_names}")
        return None

    for threshold in [30, 50, 80]:
        for size in range(1, 9):
            col_name = f'il{threshold}_p{size}'
            missing_values = income_limits_df[col_name].isnull().sum()
            if missing_values > 0:
                print(f"Number of rows with missing values in {col_name}: {missing_values}")
                return None
    try:
        income_limit_columns = [f'il{threshold}_p{size}' for threshold in [30, 50, 80] for size in range(1, 9)]
        income_limits_df[income_limit_columns] = income_limits_df[income_limit_columns].apply(pd.to_numeric, errors='coerce')
    except ValueError as e:
        print(f"Error converting columns to appropriate types: {e}")
        return None

    print("Income limits data loaded successfully and all checks passed.")
    return income_limits_df

def load_incarceration_df(file_path=None):
    if file_path is None:
        print("No incarceration data provided.")
        return None

    try:
        incarceration_df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    required_columns = ['County_Name', 'Ttl_Incarc']
    race_columns = ['Ttl_Minority_Incarc', 'Ttl_White_Incarc']

    missing_required_columns = [col for col in required_columns if col not in incarceration_df.columns]
    if missing_required_columns:
        print(f"Missing required columns: {', '.join(missing_required_columns)}. Please ensure the file has these columns.")
        return None

    missing_race_columns = [col for col in race_columns if col not in incarceration_df.columns]
    if missing_race_columns:
        print(f"Attention: Missing columns {', '.join(missing_race_columns)}. Race sampling will not be available.")

    # Remove commas and convert columns to integers
    try:
        incarceration_df['Ttl_Incarc'] = incarceration_df['Ttl_Incarc'].str.replace(',', '').astype(int)
        if 'Ttl_Minority_Incarc' in incarceration_df.columns:
            incarceration_df['Ttl_Minority_Incarc'] = incarceration_df['Ttl_Minority_Incarc'].str.replace(',', '').astype(int)
        if 'Ttl_White_Incarc' in incarceration_df.columns:
            incarceration_df['Ttl_White_Incarc'] = incarceration_df['Ttl_White_Incarc'].str.replace(',', '').astype(int)
    except ValueError as e:
        print(f"Error converting columns to integers: {e}")
        return None

    print("Incarceration data loaded successfully.")
    return incarceration_df

def load_hud_hcv_data(filepath):
    """
    Load HUD Picture of Subsidized Housing data from a CSV file and perform checks.

    Parameters:
    filepath (str): Path to the CSV file.

    Returns:
    pd.DataFrame: Loaded HUD HCV data if all checks pass.

    Notes:
    - Ensure the HUD dataset includes columns named 'Name', 'Subsidized units available',
      '% Minority', and '% White Non-Hispanic'.
    """
    try:
        # Load the huc hcv dataset
        hud_hcv_df = pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    # Check for required columns
    required_columns = ['Name', 'Subsidized units available', '% Minority', '%White Non-Hispanic']
    missing_columns = [col for col in required_columns if col not in hud_hcv_df.columns]
    if missing_columns:
        print(f"Missing required columns: {', '.join(missing_columns)}")
        print("Ensure the HUD dataset includes columns named 'Name', 'Subsidized units available', '% Minority', and '%White Non-Hispanic'.")
        return None

    # Check for missing values
    missing_values = {col: hud_hcv_df[col].isnull().sum() for col in required_columns if hud_hcv_df[col].isnull().sum() > 0}
    if missing_values:
        for col, count in missing_values.items():
            print(f"Number of rows with missing {col} values: {count}")
        return None

    print("HUD HCV data loaded successfully and all checks passed.")
    return hud_hcv_df

