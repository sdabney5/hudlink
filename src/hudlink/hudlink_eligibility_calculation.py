"""
Calculate subsidy eligibility based on household income and family size
using HUD Section 8 income limits. Adds eligibility flags for 30%, 50%, and 80% thresholds and computes
weighted eligibility counts.

Functions:

- calculate_eligibility: Merges IPUMS data with income limits, adjusts family size,
  adds eligibility flags for each threshold, and computes weighted eligibility counts.
"""

import logging


def calculate_eligibility(df, income_limits_df, weight_col, exclude_group_quarters=False):
    """
    Calculate eligibility for each household.

    Parameters:
        df (pd.DataFrame):
            The cleaned IPUMS DataFrame containing at least:
            - 'FAMSIZE' (household size)
            - 'County_Name_Alt' (county key matching income_limits_df)
            - 'ACTUAL_HH_INCOME' (household income)
            - weight_col (e.g. 'Allocated_HHWT' or 'REALHHWT') indicating the household weight.

        income_limits_df (pd.DataFrame):
            Income limits data with column 'County_Name' matching 'County_Name_Alt'
            and income limit columns named like 'il30_p1', 'il50_p1', 'il80_p1', etc.
            
        weight_col (str):
            Name of the weight column to use when computing the
            weighted eligibility counts.
            
        exclude_group_quarters (bool, optional):
            If True, zeroes out eligibility and weighted counts for any household
            where GQTYPE == 2 (institutional group quarters).

    Returns:
        pd.DataFrame:
            The merged DataFrame with added columns:
            - 'ADJUSTED_FAMSIZE' (family size capped at 8)
            - 'Eligible_at_30%', 'Eligible_at_50%', 'Eligible_at_80%'
            - 'Weighted_Eligibility_Count_30%', etc.
    """
    df = df.copy()
    df['ADJUSTED_FAMSIZE'] = df['FAMSIZE'].apply(lambda x: 8 if x > 8 else x)
    missing_counties = df.loc[
        ~df['County_Name_Alt'].isin(income_limits_df['County_Name']),
        'County_Name_Alt'
    ].unique()
    if len(missing_counties) > 0:
        logging.warning(
            f"Warning: The following counties are missing in the income limits data: "
            f"{', '.join(missing_counties)}"
        )
    merged_df = df.merge(
        income_limits_df,
        left_on='County_Name_Alt',
        right_on='County_Name',
        how='left'
    )
    merged_df.rename(
        columns={
            'County_Name_x': 'County_Name_state_abbr',
            'County_Name_y': 'County_Name'
        },
        inplace=True
    )
    thresholds = {"30%": "il30_p", "50%": "il50_p", "80%": "il80_p"}
    for threshold, prefix in thresholds.items():
        eligibility_col = f'Eligible_at_{threshold}'
        weighted_col = f'Weighted_Eligibility_Count_{threshold}'
        merged_df[eligibility_col] = merged_df.apply(
            lambda row: 1
            if row['ACTUAL_HH_INCOME'] <= row[f'{prefix}{int(row["ADJUSTED_FAMSIZE"])}']
            else 0,
            axis=1
        )
        merged_df[weighted_col] = merged_df[eligibility_col] * merged_df[weight_col]
        
    # Exclude group-quarter households if requested
    if exclude_group_quarters and 'GQTYPE' in merged_df.columns:
        mask = merged_df['GQTYPE'] == 2
        for threshold in thresholds:
            elig_col = f'Eligible_at_{threshold}'
            wt_col   = f'Weighted_Eligibility_Count_{threshold}'
            merged_df.loc[mask, [elig_col, wt_col]] = 0

    return merged_df
