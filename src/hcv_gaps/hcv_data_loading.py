"""
This module contains functions for loading required datasets.
Each function performs checks and logs validation or failure.

Functions:

1. load_ipums_data(filepath):
    - Loads IPUMS data from a CSV and checks for required columns and missing values.

2. load_crosswalk_data(filepath_2012, filepath_2022):
    - Loads MCDC crosswalk data for 2012 and 2022 from CSVs, validates columns, and normalizes allocation factors.

3. load_income_limits(filepath):
    - Loads income limits data and checks for expected HUD variable structure and missing or invalid entries.

4. load_incarceration_df(filepath):
    - Loads incarceration data and validates key columns and data integrity.

5. load_hud_hcv_data(config):
    - Loads HUD HCV data, cleans problematic codes, and generates reports if verbose.

Usage:
    import hcv_data_loading as hcv_data

    ipums_df = hcv_data.load_ipums_data("path_to_ipums_data.csv")
    crosswalk_df = hcv_data.load_crosswalk_data("path_to_crosswalk_data.csv")
    income_limits_df = hcv_data.load_income_limits("path_to_income_limits.csv")
    incarceration_df = hcv_data.load_incarceration_df("path_to_incarceration_data.csv")
    hud_hcv_df = hcv_data.load_hud_hcv_data(config)
"""

#Imports
import pandas as pd
import logging
from pandas.api import types as pd_types

logging.info("hcv_data_loading module loaded.")



def load_ipums_data(filepath: str) -> pd.DataFrame:
    """
    Load IPUMS data from a CSV file and perform variable checks.

    Parameters:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded and cleaned IPUMS data.

    Raises:
        ValueError: If the file can't be read, required columns are missing,
                    or conversions fail.
    """
    try:
        ipums_df = pd.read_csv(filepath)
    except Exception as e:
        raise ValueError(f"Error loading IPUMS file: {e}")

    # Required columns for downstream processing
    required_columns = [
        'PUMA', 'COUNTYICP', 'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
        'HHWT', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER',
        'NFAMS', 'FAMUNIT', 'CBSERIAL'
    ]
    missing = [c for c in required_columns if c not in ipums_df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    # Report any rows with missing PUMA or COUNTYICP
    n_null_puma = ipums_df['PUMA'].isna().sum()
    n_null_cty = ipums_df['COUNTYICP'].isna().sum()
    if n_null_puma or n_null_cty:
        raise ValueError(
            f"Missing values detected: PUMA nulls={n_null_puma}, "
            f"COUNTYICP nulls={n_null_cty}"
        )

    # Convert and normalize types
    try:
        # Normalize PUMA: strip, drop leading zeros
        ipums_df['PUMA'] = (
            ipums_df['PUMA']
            .astype(str)
            .str.strip()
            .str.lstrip('0')
        )
        # Standardize COUNTYICP
        ipums_df['COUNTYICP'] = ipums_df['COUNTYICP'].astype(str).str.strip()

        # Convert weights and income columns to numeric
        ipums_df['HHWT'] = pd.to_numeric(ipums_df['HHWT'], errors='coerce')
        income_cols = [
            'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
            'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER'
        ]
        ipums_df[income_cols] = ipums_df[income_cols].apply(
            lambda col: pd.to_numeric(col, errors='coerce')
        )
    except Exception as e:
        raise ValueError(f"Error converting IPUMS columns: {e}")

    logging.info("IPUMS data loaded and cleaned: %d rows, %d columns", *ipums_df.shape)
    return ipums_df


def load_crosswalk_data(filepath_2012: str, filepath_2022: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load, validate, and normalize the 2012 and 2022 MCDC crosswalks.

    Parameters:
        filepath_2012 (str): Path to the 2012 crosswalk CSV.
        filepath_2022 (str): Path to the 2022 crosswalk CSV.

    Returns:
        Tuple of (crosswalk_2012_df, crosswalk_2022_df) with:
          - 'PUMA' as stripped strings without leading zeros
          - 'allocation factor' as floats
          - duplicate rows dropped
          - allocation factors normalized to sum to 1 per PUMA

    Raises:
        ValueError: If required columns are missing or allocation sums are invalid.
    """
    try:
        cw12 = pd.read_csv(filepath_2012)
        cw22 = pd.read_csv(filepath_2022)
    except Exception as e:
        raise ValueError(f"Error reading crosswalk files: {e}")

    required = ['State code', 'PUMA', 'County code', 'State abbr.', 'County_Name', 'allocation factor']
    for df, year in ((cw12, 2012), (cw22, 2022)):
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"{year} crosswalk missing columns: {missing}")
        if df[required].isnull().any().any():
            details = df[required].isnull().sum()
            raise ValueError(f"{year} crosswalk has nulls:\n{details}")

    # Normalize PUMA and allocation factor in both dataframes
    for cw in (cw12, cw22):
        cw['PUMA'] = (
            cw['PUMA']
            .astype(str)
            .str.strip()
            .str.lstrip('0')
        )
        cw['allocation factor'] = pd.to_numeric(cw['allocation factor'], errors='raise')

        # Drop duplicates and normalize within each PUMA
        cw.drop_duplicates(subset=['PUMA', 'County_Name'], inplace=True)
        cw['allocation factor'] /= cw.groupby('PUMA')['allocation factor'].transform('sum')

        # Verify sums to 1
        sums = cw.groupby('PUMA')['allocation factor'].sum().round(6)
        bad = sums[sums != 1]
        if not bad.empty:
            raise ValueError(f"Allocation factors do not sum to 1 for some PUMAs:\n{bad}")

    logging.info("Loaded and cleaned crosswalks: 2012 (%d PUMAs), 2022 (%d PUMAs)",
                 cw12['PUMA'].nunique(), cw22['PUMA'].nunique())
    return cw12, cw22
import logging
import pandas as pd




def load_income_limits(filepath, agg_method="min"):
    """
    Load income limits data from a CSV file and perform validation checks.

    Parameters:
    filepath (str): Path to the CSV file.
    agg_method (str): How to collapse multiple rows per county. One of {"min","max","median","mean"}.

    Returns:
    pd.DataFrame: Loaded, validated (and if needed, deduplicated) income limits data.

    Raises:
    ValueError: If required columns are missing, data contains missing values,
                invalid data types are found, or agg_method is invalid.
    """
    try:
        # Load the dataset
        income_limits_df = pd.read_csv(filepath)

        # Define required columns
        required_columns = ['County_Name'] + [
            f'il{threshold}_p{size}'
            for threshold in [30, 50, 80]
            for size in range(1, 9)
        ]

        # Check for missing columns
        missing_columns = [col for col in required_columns if col not in income_limits_df.columns]
        if missing_columns:
            raise ValueError(f"Income limits data is missing required columns: {missing_columns}")

        # Check for missing County_Name
        missing_county_names = income_limits_df['County_Name'].isnull().sum()
        if missing_county_names > 0:
            raise ValueError(f"{missing_county_names} rows with missing 'County_Name'")

        # Check for any other missing values
        missing_vals = {
            col: income_limits_df[col].isnull().sum()
            for col in required_columns
            if income_limits_df[col].isnull().sum() > 0
        }
        if missing_vals:
            info = "; ".join(f"{col}: {cnt}" for col, cnt in missing_vals.items())
            raise ValueError(f"Missing values found: {info}")

        # Convert the limit columns to numeric
        limit_cols = required_columns[1:]
        income_limits_df[limit_cols] = income_limits_df[limit_cols].apply(
            pd.to_numeric, errors='coerce'
        )

        # Re-check for non-numeric / NaNs
        bad = income_limits_df[limit_cols].isnull().sum().sum()
        if bad > 0:
            cols = [c for c in limit_cols if income_limits_df[c].isnull().any()]
            raise ValueError(f"Invalid or non-numeric in columns: {cols}")

        if agg_method not in {"min", "max", "median", "mean"}:
            raise ValueError(f"Unknown agg_method '{agg_method}'")

        if income_limits_df.duplicated(subset=["County_Name"]).any():
            logging.warning(
                "Multiple rows for County_Name found in %s; collapsing with %s()",
                filepath, agg_method
            )
            agg_dict = {c: agg_method for c in limit_cols}
            # keep County_Name as-is
            agg_dict["County_Name"] = "first"
            income_limits_df = (
                income_limits_df
                .groupby("County_Name", as_index=False)
                .agg(agg_dict)
            )

    except Exception as e:
        raise ValueError(f"Error loading/validating income limits from {filepath}: {e}")

    logging.info("Income limits data loaded successfully.")
    return income_limits_df



def load_incarceration_df(filepath=None):
    """
    Load incarceration data from a CSV file
    
    Parameters:
    filepath (str or None): Path to the CSV file.

    Returns
    -------
    pd.DataFrame or None

    Raises
    ------
    ValueError
        If the file is missing required columns, or if County_Name
        is not textual or contains "0".
    """
    if filepath is None:
        logging.info("No incarceration data provided.")
        return None

    # Only load the columns we need, force County_Name to pandas StringDtype
    needed_cols = [
        "State",
        "County_Name",
        "Ttl_Incarc",
        "Ttl_Minority_Incarc",
        "Ttl_White_Incarc",
    ]

    try:
        df = pd.read_csv(
            filepath,
            usecols=needed_cols,
            dtype={"County_Name": "string"},
            low_memory=False,
        )
    except Exception as e:
        raise ValueError(f"Failed to read incarceration CSV at {filepath!r}: {e}")

    # Check that all needed columns are present
    missing = [c for c in needed_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Incarceration data missing columns: {missing!r}")

    # Ensure County_Name is truly a string dtype
    if not pd_types.is_string_dtype(df["County_Name"]):
        raise ValueError(
            f"'County_Name' must be text, but got dtype {df['County_Name'].dtype}"
        )

    # Guard against the “all zeros” bug: if any entry is exactly "0", it's wrong
    zero_mask = df["County_Name"] == "0"
    if zero_mask.any():
        bad_idxs = df.index[zero_mask][:5].tolist()
        raise ValueError(
            f"Found literal '0' in County_Name at rows {bad_idxs}; "
            "please verify the CSV path and contents."
        )

    logging.info(
        "Loaded incarceration data from %r (%d rows)",
        filepath,
        len(df)
    )
    return df



def load_hud_hcv_data(config):
    """
    Load and clean the HUD PSH CSV for downstream linkage.

    - Reads the full CSV at config['hud_hcv_data_path'].
    - Converts all non-identifier columns to numeric (stripping commas,
      coercing errors to NaN, preserving negative codes).
    - Normalizes raw 'program_label' values via an in-function lookup,
      writing the cleaned name back into 'program_label'.

    Parameters:
        config (dict): Must contain:
            - 'hud_hcv_data_path': Path to the HUD CSV file.

    Returns:
        pd.DataFrame: Cleaned HUD PSH DataFrame with:
            - Original identifier columns as strings.
            - All other columns as floats.
            - A cleaned 'program_label' column only.
    """
    path = config['hud_hcv_data_path']
    try:
        df = pd.read_csv(path, dtype=str)
    except Exception as e:
        raise ValueError(f"Could not read HUD PSH file at {path}: {e}")

    # Columns that should remain as strings
    id_cols = {
        'gsl','states','entities','sumlevel',
        'program_label','program','sub_program',
        'name','code','fedhse','cbsa','place','state','County_norm'
    }

    # Convert everything else to numeric
    for col in df.columns:
        if col in id_cols:
            continue
        df[col] = (
            df[col]
              .str.replace(",", "", regex=False)
              .pipe(pd.to_numeric, errors='coerce')
        )

    # In-place mapping of program_label → canonical names
    program_map = {
        "All HUD":                     "Summary of All HUD Programs",
        "MF/Other":                    "Multi-Family Other",
        "MR":                          "Mod Rehab",
        "PH":                          "Public Housing",
        "S236":                        "Section 236",
        "S8":                          "Section 8 NC/SR",
        "VO":                          "Housing Choice Vouchers",
        "LIHTC":                       "LIHTC",
        "Housing Choice Vouchers":     "Housing Choice Vouchers",
        "Section 8 NC/SR":             "Section 8 NC/SR",
        "Summary of All HUD Programs": "Summary of All HUD Programs",
        # extend with any other historical variants…
    }
    df['program_label'] = (
        df['program_label']
          .map(program_map)
          .fillna(df['program_label'])
    )

    return df
