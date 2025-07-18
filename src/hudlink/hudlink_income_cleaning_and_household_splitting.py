"""
hudlink_income_cleaning_and_household_splitting.py
Performs income data cleaning and multi-family household splitting.

This module contains functions for cleaning income data and splitting multifamily households
into distinct families within the IPUMS dataset.
Functions:

- clean_single_family_income_data: Cleans income data for single-family households.
- split_multifamily_households: Splits multifamily households and adjusts weights.
- process_multi_family_income_data: Aggregates income data for each separated family.
"""

import logging


def clean_single_family_income_data(df):
    """
    Clean income data for single-family households.

    Parameters:
        df (pd.DataFrame): The input dataframe containing household data.

    Returns:
        pd.DataFrame: The updated dataframe with cleaned income data for single-family households.

    Notes:
        - Replaces placeholder values (e.g., 9999999) with 0.
        - Populates the 'ACTUAL_HH_INCOME' column using FTOTINC, HHINCOME, or other sources.
    """
    df[['HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST',
        'INCRETIR', 'INCSUPP', 'INCOTHER']] = df[['HHINCOME', 'FTOTINC',
        'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP',
        'INCOTHER']].astype(float)

    df.replace([9999999, 999999, 999998, 99999], 0, inplace=True)

    single_family = df[df['NFAMS'] == 1]
    null_income_columns = ['HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
                           'INCINVST', 'INCRETIR', 'INCSUPP', 'INCOTHER']

    # Check for single-family households with no income data at all
    problem_rows = single_family[single_family[null_income_columns].isnull().all(axis=1)]
    if not problem_rows.empty:
        logging.warning(f"{len(problem_rows)} single-family households have no usable income data.")

    # Populate 'ACTUAL_HH_INCOME'
    hh_income_ftotinc_both_notnull = df[(df['HHINCOME'].notnull()) & (df['FTOTINC'].notnull())]
    df.loc[hh_income_ftotinc_both_notnull.index, 'ACTUAL_HH_INCOME'] = hh_income_ftotinc_both_notnull['FTOTINC']

    hhincome_null_ftotinc_notnull = single_family[(single_family['HHINCOME'].isnull()) &
                                                  (single_family['FTOTINC'].notnull())]
    df.loc[hhincome_null_ftotinc_notnull.index, 'ACTUAL_HH_INCOME'] = hhincome_null_ftotinc_notnull['FTOTINC']

    ftotinc_null_hhincome_notnull = single_family[(single_family['FTOTINC'].isnull()) &
                                                  (single_family['HHINCOME'].notnull())]
    df.loc[ftotinc_null_hhincome_notnull.index, 'ACTUAL_HH_INCOME'] = ftotinc_null_hhincome_notnull['HHINCOME']

    # Use other income sources if both HHINCOME and FTOTINC are null
    hhincome_ftotinc_null_others_notnull = single_family[
        (single_family[['HHINCOME', 'FTOTINC']].isnull().all(axis=1)) &
        (single_family[null_income_columns[2:]].notnull().any(axis=1))
    ]
    if not hhincome_ftotinc_null_others_notnull.empty:
        logging.warning(f"{len(hhincome_ftotinc_null_others_notnull)} single-family households rely on other income sources.")

    return df


def split_multifamily_households(df):
    """
    Split multifamily households and adjust household weights.

    Parameters:
        df (pd.DataFrame): The input dataframe containing census data.

    Returns:
        pd.DataFrame: The updated dataframe with split households and adjusted weights.

    Notes:
        - Creates FAMILYNUMBER for each unique family.
        - Renames NFAMS to NFAMS_B4_SPLIT.
        - Adjusts REALHHWT for multifamily cases by dividing Allocated_HHWT by NFAMS_B4_SPLIT.
    """
    df[['HHWT', 'Allocated_HHWT', 'NFAMS']] = df[['HHWT', 'Allocated_HHWT', 'NFAMS']].astype(float)

    # Count households before split
    serial = df.drop_duplicates(subset=["CBSERIAL"])
    pre_split_households = serial["HHWT"].sum()
    multifamily_households = serial.loc[serial["NFAMS"] > 1, "HHWT"].sum()

    # Correct FAMUNIT for single-family households
    df.loc[(df['NFAMS'] == 1) & df['FAMUNIT'].isin([0, '00', None]), 'FAMUNIT'] = 1

    # Create a unique identifier for each family
    df['FAMILYNUMBER'] = df['CBSERIAL'].astype(str) + df['FAMUNIT'].astype(str) + df['County_Name']

    # Rename NFAMS to track original number of families
    df.rename(columns={'NFAMS': 'NFAMS_B4_SPLIT'}, inplace=True)
    df['NFAMS_B4_SPLIT'] = df['NFAMS_B4_SPLIT'].astype(float)

    # Adjust household weight for split families
    df['REALHHWT'] = (df['Allocated_HHWT'] / df['NFAMS_B4_SPLIT']).round(6)

    # Count families after split
    post_split_families = df.drop_duplicates(subset=["FAMILYNUMBER"])["REALHHWT"].sum()

    logging.info(f"Households before split: {pre_split_households}")
    logging.info(f"Multifamily households before split: {multifamily_households}")
    logging.info(f"Households after split: {post_split_families}")

    return df


def process_multi_family_income_data(df):
    """
    Process and clean income variables for previously multifamily households.

    Parameters:
        df (pd.DataFrame): The input DataFrame containing household data.

    Returns:
        pd.DataFrame: The updated DataFrame with cleaned income variables.

    Notes:
        - Identifies previously multifamily families (NFAMS_B4_SPLIT > 1).
        - Populates ACTUAL_HH_INCOME using FTOTINC if available.
        - Otherwise sums other available income columns at the family level.
    """
    multi_family_rows = df[df['NFAMS_B4_SPLIT'] > 1]
    income_columns = [
        'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
        'INCINVST', 'INCRETIR', 'INCSUPP', 'INCOTHER', 'INCEARN'
    ]

    # Check for families with no income data at all
    all_null_income = multi_family_rows[multi_family_rows[income_columns].isnull().all(axis=1)]
    if not all_null_income.empty:
        logging.warning(f"{len(all_null_income)} rows from multifamily households have no usable income data.")

    # Fill ACTUAL_HH_INCOME where FTOTINC is present
    ftotinc_notnull = multi_family_rows[multi_family_rows['FTOTINC'].notnull()]
    df.loc[ftotinc_notnull.index, 'ACTUAL_HH_INCOME'] = ftotinc_notnull['FTOTINC']

    # For the remainder, sum other income sources at the personal level
    ftotinc_null = multi_family_rows[multi_family_rows['FTOTINC'].isnull()]
    df.loc[ftotinc_null.index, 'OTHERINCOME_PERSONAL'] = ftotinc_null[income_columns[2:]].sum(axis=1)

    # Aggregate OTHERINCOME_PERSONAL at the family level
    other_income_by_family = df.groupby('FAMILYNUMBER')['OTHERINCOME_PERSONAL'].sum()
    df['OTHERINCOME_FAMILY'] = df['FAMILYNUMBER'].map(other_income_by_family)

    # Fill ACTUAL_HH_INCOME where OTHERINCOME_FAMILY is available
    rows_to_fill = df[df['OTHERINCOME_FAMILY'].notnull() & df['ACTUAL_HH_INCOME'].isnull()]
    df.loc[rows_to_fill.index, 'ACTUAL_HH_INCOME'] = rows_to_fill['OTHERINCOME_FAMILY']

    return df
