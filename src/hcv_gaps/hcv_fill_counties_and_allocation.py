"""
hcv_fill_counties_and_allocation.py
Fills missing county values and allocates household weights using PUMA-to-county crosswalks.

This module fills missing county values in the IPUMS dataset by matching PUMA values to counties
using MCDC Geocorr crosswalk data. Since some PUMAs overlap multiple counties, this module also
allocates household weights (`HHWT`) based on population-based allocation factors.

Functions:

1. fill_missing_county_values(ipums_df, crosswalk_2012_df, crosswalk_2022_df):
    - Matches PUMA values in the IPUMS dataset to counties using 2012 and 2022 crosswalk data.
    - Allocates household weights (`HHWT`) for PUMAs that span multiple counties.
    - Standardizes county names for consistency in later processing.
    - Logs any unmatched PUMAs for debugging.

Usage:
To use, import this module and call `fill_missing_county_values` with the required datasets.

Example:
    import hcv_fill_counties_and_allocation as hcv_allocation

    ipums_df = load_ipums_data('path_to_ipums_data.csv')
    crosswalk_2012_df, crosswalk_2022_df = load_crosswalk_data('crosswalk_2012.csv', 'crosswalk_2022.csv')

    ipums_df = hcv_allocation.fill_missing_county_values(ipums_df, crosswalk_2012_df, crosswalk_2022_df)
"""

import pandas as pd
import logging

logging.info("This is a log message from hcv_fill_counties_and_allocation.py")

def fill_missing_county_values(ipums_df, crosswalk_2012_df, crosswalk_2022_df):
    """
    Fill missing county values in the IPUMS dataframe using separate 2012 and 2022 crosswalk datasets.
    Allocate household weights (HHWT) to counties based on the allocation factor.

    Parameters:
    -------
    ipums_df : pd.DataFrame
        The IPUMS dataframe containing PUMA, COUNTYICP, HHWT, and MULTYEAR columns.
    crosswalk_2012_df : pd.DataFrame
        The 2012 crosswalk dataframe containing PUMA (2012), allocation factor, and county information.
    crosswalk_2022_df : pd.DataFrame
        The 2022 crosswalk dataframe containing PUMA (2022), allocation factor, and county information.

    Returns:
    -------
    pd.DataFrame
        The updated IPUMS dataframe with counties filled and `Allocated_HHWT` calculated.
    """
    # Copy the original dataframe to avoid modifying in place
    ipums_df_copy = ipums_df.copy()

    try:
        # Ensure PUMA column types match
        ipums_df_copy['PUMA'] = ipums_df_copy['PUMA'].astype(str).str.strip()
        crosswalk_2012_df['PUMA'] = crosswalk_2012_df['PUMA'].astype(str).str.strip()
        crosswalk_2022_df['PUMA'] = crosswalk_2022_df['PUMA'].astype(str).str.strip()

        # Split IPUMS data into two subsets based on MULTYEAR
        ipums_2012_df = ipums_df_copy[ipums_df_copy['MULTYEAR'] <= 2021]
        ipums_2022_df = ipums_df_copy[ipums_df_copy['MULTYEAR'] >= 2022]

        # Merge IPUMS 2012 data with crosswalk 2012
        merged_2012_df = pd.merge(ipums_2012_df, crosswalk_2012_df, on='PUMA', how='left')
        logging.info('merged 2012 df columns *****************************')
        logging.info(merged_2012_df.columns)

        # Calculate Allocated_HHWT for 2012
        merged_2012_df['Allocated_HHWT'] = merged_2012_df['HHWT'] * merged_2012_df['allocation factor']

        # Merge IPUMS 2022 data with crosswalk 2022
        merged_2022_df = pd.merge(ipums_2022_df, crosswalk_2022_df, on='PUMA', how='left')
        logging.info('merged 2022 df columns *****************************')
        logging.info(merged_2022_df.columns)
        logging.info('***********************************************')

        # Calculate Allocated_HHWT for 2022
        merged_2022_df['Allocated_HHWT'] = merged_2022_df['HHWT'] * merged_2022_df['allocation factor']

        # Concatenate the two merged subsets back together
        merged_df = pd.concat([merged_2012_df, merged_2022_df], ignore_index=True)

        # Fill missing County_Name values with "Unknown County"
        merged_df['County_Name'].fillna('Unknown County', inplace=True)

        # List unmatched PUMAs for debugging
        unmatched_pumas = merged_df.loc[merged_df['County_Name'] == 'Unknown County', 'PUMA'].unique()
        if len(unmatched_pumas) > 0:
            logging.info(f"WARNING: There are unmatched PUMAs in this dataset. Unmatched PUMAs: {list(unmatched_pumas)}")

        # Standardize county names for compatibility with later processing
        merged_df['County_Name_Alt'] = merged_df['County_Name'].apply(
            lambda x: x[:-2] + 'County' if x != 'Unknown County' else x
        )

        
        return merged_df

    except KeyError as e:
        logging.info(f"KeyError: {e}. Please ensure the input dataframes contain the necessary columns.")
        return ipums_df_copy  # Return original dataframe on failure
    except Exception as e:
        logging.info(f"An error occurred: {e}")
        return ipums_df_copy  # Return original dataframe on failure
    
    
