import pandas as pd
import logging

def fill_missing_county_values(ipums_df, crosswalk_2012_df, crosswalk_2022_df):
    """
    Fill missing county values in the IPUMS DataFrame and compute Allocated_HHWT.

    Parameters:
        ipums_df (pd.DataFrame):
            IPUMS person‐level data containing at least the columns
            'PUMA', 'COUNTYICP', 'HHWT', and 'MULTYEAR'.
        crosswalk_2012_df (pd.DataFrame):
            2012 MCDC Geocorr crosswalk with columns 'PUMA', 'allocation factor', and 'County_Name'.
        crosswalk_2022_df (pd.DataFrame):
            2022 MCDC Geocorr crosswalk with columns 'PUMA', 'allocation factor', and 'County_Name'.

    Returns:
        pd.DataFrame:
            A new DataFrame with:
              - 'Allocated_HHWT' computed for each row
              - 'County_Name' filled (or set to 'Unknown County')
              - 'County_Name_Alt' standardized (e.g., ends with 'County')
            If a merge error occurs, returns a copy of the original IPUMS DataFrame.
    """
    df_copy = ipums_df.copy()

    try:
        # 1) Normalize PUMA codes on all three DataFrames
        df_copy['PUMA'] = df_copy['PUMA'].astype(str).str.strip()
        crosswalk_2012_df['PUMA'] = crosswalk_2012_df['PUMA'].astype(str).str.strip()
        crosswalk_2022_df['PUMA'] = crosswalk_2022_df['PUMA'].astype(str).str.strip()

        # 2) If any record was interviewed in 2023 or later:
        #    use 2022 crosswalk for everyone.
        if (df_copy['MULTYEAR'].astype(int) >= 2023).any():
            merged = pd.merge(
                df_copy,
                crosswalk_2022_df,
                on='PUMA',
                how='left'
            )
            merged['Allocated_HHWT'] = merged['HHWT'] * merged['allocation factor']

        else:
            # 3) Otherwise (no 2023+ rows), split at MULTYEAR 2019/2020
            df_2012  = df_copy[df_copy['MULTYEAR'].astype(int) <= 2019]
            df_2022  = df_copy[df_copy['MULTYEAR'].astype(int) >= 2020]

            # merge each subset
            merged_2012 = pd.merge(
                df_2012,
                crosswalk_2012_df,
                on='PUMA',
                how='left'
            )
            merged_2012['Allocated_HHWT'] = (
                merged_2012['HHWT'] * merged_2012['allocation factor']
            )

            merged_2022 = pd.merge(
                df_2022,
                crosswalk_2022_df,
                on='PUMA',
                how='left'
            )
            merged_2022['Allocated_HHWT'] = (
                merged_2022['HHWT'] * merged_2022['allocation factor']
            )

            # recombine
            merged = pd.concat([merged_2012, merged_2022], ignore_index=True)

        # 4) Fill missing County_Name
        merged['County_Name'] = merged['County_Name'].fillna('Unknown County')

        # 5) Warn about any truly unmatched
        unmatched = merged.loc[merged['County_Name']=='Unknown County', 'PUMA'].unique()
        if len(unmatched):
            logging.warning("Unmatched PUMAs found: %s", list(unmatched))

        # 6) Standardize County_Name_Alt
        merged['County_Name_Alt'] = merged['County_Name'].apply(
            lambda x: x[:-2] + 'County' if x != 'Unknown County' else x
        )

        return merged

    except KeyError as e:
        logging.error(
            "KeyError in fill_missing_county_values: %s. Check that input DataFrames have the required columns.",
            e
        )
        return df_copy

    except Exception as e:
        logging.error("Unexpected error in fill_missing_county_values: %s", e)
        return df_copy
