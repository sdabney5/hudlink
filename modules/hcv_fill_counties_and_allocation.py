"""
This module includes a function to fill in missing county information in an IPUMS dataset using MCDC data
It allocates rows to individual counties based on allocation factors for multi-county PUMAs.

Function:

1. fill_missing_county_values(ipums_df, crosswalk_df):
    Fills missing county values in the IPUMS dataframe using the crosswalk dataset and allocates county-grouped records
    to individual counties based on allocation factors.

Usage:
To use, simply import this module and call the function with the IPUMS and crosswalk dataframes as arguments.
The function will return the modified IPUMS dataframe with filled counties and allocated rows.

Example:
    import hcv_fill_counties_and_allocation as hcv_allocation

    ipums_df = hcv_allocation.fill_missing_county_values(ipums_df, crosswalk_df)
"""

# Imports
import pandas as pd

def fill_missing_county_values(ipums_df, crosswalk_df):
    """
    Fill missing county values in the IPUMS dataframe using the crosswalk dataset and allocate rows to individual counties.

    This function takes the IPUMS dataframe and fills in missing county values using the crosswalk dataset. It also allocates
    rows to individual counties based on allocation factors for multi-county PUMAs.

    Parameters:
    -------
    ipums_df : pd.DataFrame
        The IPUMS dataframe containing PUMA and COUNTYICP columns.
    crosswalk_df : pd.DataFrame
        The crosswalk dataframe containing PUMA, county codes, allocation factors, and county names.

    Returns:
    -------
    pd.DataFrame
        The updated IPUMS dataframe with missing county values filled and county names populated.

    Notes:
    -----
    - Ensure the crosswalk dataset contains the necessary columns: 'PUMA', 'County code', 'County name', and 'allocation_factor'.
    - The function will print a warning if there are unmatched PUMAs in the crosswalk dataset. This might indicate a mismatch
      between PUMA versions (e.g., 2022 PUMAs used instead of 2012 PUMAs).
    - The COUNTYICP column is dropped from the resulting dataframe to avoid confusion.

    Example:
    -------
    >>> import hcv_fill_counties_and_allocation as hcv_allocation
    >>> ipums_df = hcv_allocation.fill_missing_county_values(ipums_df, crosswalk_df)
    """
    # Create a copy of the ipums_df
    ipums_df_copy = ipums_df.copy()

    try:
        # Ensure PUMA column data types match
        ipums_df_copy['PUMA'] = ipums_df_copy['PUMA'].astype(str)
        crosswalk_df['PUMA'] = crosswalk_df['PUMA'].astype(str)

        # Merge the dataframes on PUMA
        merged_df = pd.merge(ipums_df_copy, crosswalk_df, on='PUMA', how='left')

        # Check if the merge was successful
        if merged_df.empty:
            raise ValueError("Merge produced an empty dataframe. Double check the ipums and crosswalk dfs.")

        # Rename columns
        if 'County code' not in merged_df.columns or 'County name' not in merged_df.columns or 'allocation_factor' not in merged_df.columns:
            raise KeyError("Expected columns 'County code', 'County name', or 'allocation_factor' not found in merged dataframe.")

        merged_df = merged_df.rename(columns={
            'PUMA_Name': 'County_Group',
            'County code': 'COUNTYICP',
            'County name': 'County_Name'
        })

        # Calculate the allocated weight
        merged_df['Allocated_HHWT'] = merged_df['HHWT'] * merged_df['allocation_factor']

        # Fill missing County_Name values with "Unknown County"
        merged_df['County_Name'].fillna('Unknown County', inplace=True)

        # List the PUMAs that were assigned "Unknown County"
        num_missing_counties = (merged_df['County_Name'] == 'Unknown County').sum()
        if num_missing_counties > 0:
            unmatched_pumas = merged_df.loc[merged_df['County_Name'] == 'Unknown County', 'PUMA'].unique()
            print(f"Unmatched PUMAs: {list(unmatched_pumas)}")
            print("WARNING: There are unmatched PUMAs in this dataset. This is likely due to using the wrong crosswalk data (e.g. using 2022 PUMAs when 2012 PUMAs are required).")

        # Standardize county names to match the hud_hcv_df in later gap calculation step
        merged_df['County_Name_Alt'] = merged_df['County_Name'].apply(lambda x: x[:-2] + 'County' if x != 'Unknown County' else x)

        # Drop the COUNTYICP column
        merged_df = merged_df.drop(columns=['COUNTYICP'])

    except KeyError as e:
        print(f"KeyError: {e}. Please ensure the input dataframes contain the necessary columns.")
        return ipums_df_copy  # Return the original ipums_df
    except Exception as e:
        print(f"An error occurred: {e}")
        return ipums_df_copy  # Return the original ipums_df



    return merged_df
