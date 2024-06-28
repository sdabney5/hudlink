"""
hcv_eligibility_calculation.py

This module contains the function to calculate Housing Choice Voucher (HCV) eligibility based on household income
and family size using the income limits for each county. The eligibility is determined for 30%, 50%, and 80% of
the median income levels as defined by HUD. It also calculates weighted eligibility counts by race.

Functions:

1. calculate_hcv_eligibility(df, income_limits_df):
    Merges the IPUMS dataset with income limits data, adjusts family size, and adds eligibility columns for each
    income threshold (30%, 50%, 80%). It also calculates weighted eligibility counts by race.

Usage:
To use, import this module and call the `calculate_hcv_eligibility` function with the cleaned IPUMS dataframe and
the income limits dataframe.

Example:
    import hcv_eligibility_calculation as hcv_eligibility

    ipums_df = load_ipums_data('path_to_ipums_data.csv')
    income_limits_df = load_income_limits('path_to_income_limits.csv')

    ipums_df = hcv_eligibility.calculate_hcv_eligibility(ipums_df, income_limits_df)
"""

#imports
import pandas as pd

def calculate_hcv_eligibility(df, income_limits_df):
    """
    Calculate Housing Choice Voucher (HCV) eligibility based on household income and family size.

    This function calculates HCV eligibility for households based on their income and family size, relative to
    the income limits for their county. It adds eligibility columns for thresholds at 30%, 50%, and 80% of
    the median income for the area, and calculates weighted eligibility counts by race.

    Parameters:
    ----------
    df : pd.DataFrame
        The cleaned and prepared IPUMS data.
    income_limits_df : pd.DataFrame
        The income limits data with columns named according to the HUD API convention.

    Returns:
    -------
    pd.DataFrame
        The DataFrame with added eligibility columns and weighted eligibility counts by race.

    Notes:
    -----
    - Ensure the income limits dataset follows the HUD API naming convention (e.g., 'il50_p1', 'il30_p1', 'il80_p1').
    - Adjusts family size to a maximum of 8, as HUD's income limits max out at a family size of 8.
    - Merges the IPUMS dataset with income limits data on the 'County_Name_Alt' column.
    - Adds eligibility columns for each income threshold (30%, 50%, 80%) based on household income and family size.
    - Calculates weighted eligibility counts by race, distinguishing between white and minority households.
    """

    # Create a copy of the cleaned IPUMS df
    df = df.copy()

    # Adjust family size, capping at 8 (because HUD's income limits max out at a family size of 8)
    df['ADJUSTED_FAMSIZE'] = df['FAMSIZE'].apply(lambda x: 8 if x > 8 else x)

    # Check for missing County_Name_Alt values
    missing_counties = df.loc[~df['County_Name_Alt'].isin(income_limits_df['County_Name']), 'County_Name_Alt'].unique()
    if len(missing_counties) > 0:
        print(f"Warning: The following counties are missing in the income limits data: {', '.join(missing_counties)}")

    # Merge dataframes on the 'County_Name_Alt' column to get the income limits for each household
    merged_df = df.merge(income_limits_df, left_on='County_Name_Alt', right_on='County_Name', how='left')

    # Rename the columns to avoid conflicts
    merged_df.rename(columns={'County_Name_x': 'County_Name_state_abbr', 'County_Name_y': 'County_Name'}, inplace=True)

    # Define income limit prefixes based on HUD API convention
    thresholds = {
        "30%": "il30_p",
        "50%": "il50_p",
        "80%": "il80_p"
    }

    # Determine eligibility for each income threshold and calculate weighted eligibility counts
    for threshold, prefix in thresholds.items():
        eligibility_col = f'Eligible_at_{threshold}'
        weighted_col = f'Weighted_Eligibility_Count_{threshold}'
        white_weighted_col = f'Weighted_White_HH_Eligibility_Count_{threshold}'
        minority_weighted_col = f'Weighted_Minority_HH_Eligibility_Count_{threshold}'

        # Determine eligibility using the income limits
        merged_df[eligibility_col] = merged_df.apply(
            lambda row: 1 if row['ACTUAL_HH_INCOME'] <= row[f'{prefix}{int(row["ADJUSTED_FAMSIZE"])}'] else 0, axis=1
        )

        # Calculate weighted eligibility count
        merged_df[weighted_col] = merged_df[eligibility_col] * merged_df['Allocated_HHWT']

        # Calculate weighted eligibility counts by race
        merged_df[white_weighted_col] = merged_df[weighted_col] * merged_df['White_HH'].apply(lambda x: 1 if x else 0)
        merged_df[minority_weighted_col] = merged_df[weighted_col] * merged_df['White_HH'].apply(lambda x: 0 if x else 1)

    return merged_df