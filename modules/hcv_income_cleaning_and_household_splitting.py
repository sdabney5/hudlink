"""
hcv_income_cleaning_and_household_splitting.py
Performs income data cleaning and multi-family household splitting.

This module contains functions for cleaning income data and splitting multifamily households
into distinct families within the IPUMS dataset. These functions are essential for accurately
determining Housing Choice Voucher (HCV) eligibility by ensuring that eligibility of individual
families within multi-family households is considered independently.

Functions:

1. clean_single_family_income_data(df):
    Examines and cleans income data for single-family households. This function addresses
    missing values and ensures that 'ACTUAL_HH_INCOME' is populated correctly.

2. split_multifamily_households(df):
    Splits multifamily households into individual families by creating unique family numbers.
    It also adjusts the household weight ('HHWT') to reflect the division into multiple families,
    creating a new column 'REALHHWT'.

3. process_multi_family_income_data(df):
    Processes and cleans income data for previously multifamily households. This
    ensures that all income sources are considered and aggregated correctly into a new column:
    'ACTUAL_HH_INCOME'.

Usage:
To use, import this module and call the functions with the IPUMS dataframe as the argument.
The functions will return the modified dataframe with cleaned income data and separated families
(multi-family households split into single households).

Example:
    import hcv_income_cleaning_and_household_splitting as hcv_cleaning

    ipums_df = hcv_cleaning.clean_single_family_income_data(ipums_df)
    ipums_df = hcv_cleaning.split_multifamily_households(ipums_df)
    ipums_df = hcv_cleaning.process_multi_family_income_data(ipums_df)

"""

#imports
import pandas as pd

def clean_single_family_income_data(df):
    """
    Clean income data for single-family households.

    This function examines and cleans income data for single-family households. It addresses missing values
    and ensures that the 'ACTUAL_HH_INCOME' column is populated correctly by using available income columns.

    Parameters:
    ----------
    df : pd.DataFrame
        The input dataframe containing household data.

    Returns:
    -------
    pd.DataFrame
        The updated dataframe with cleaned income data for single-family households.

    Notes:
    -----
    - This function replaces certain placeholder values (e.g., 9999999) with 0.
    - The function populates the 'ACTUAL_HH_INCOME' column based on available income columns.

    Verification:
    -------------
    Verified on 2024-06-25 with:
    - test_data_1
    - production_data
    """

    df.replace([9999999, 999999, 999998, 99999], 0, inplace=True)
    single_family = df[df['NFAMS'] == 1]

    null_income_columns = ['HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCOTHER']

    all_null_income = single_family[single_family[null_income_columns].isnull().all(axis=1)]
    print(f"Number of single family rows with all null income values: {len(all_null_income)}")

    hh_income_ftotinc_both_notnull = df[(df['HHINCOME'].notnull()) & (df['FTOTINC'].notnull())]
    print(f'Single Family rows that have both HHINCOME and FTOTINC values: {len(hh_income_ftotinc_both_notnull)}')

    print("Indices with both HHINCOME and FTOTINC not null:")
    print(hh_income_ftotinc_both_notnull.index)

    df.loc[hh_income_ftotinc_both_notnull.index, 'ACTUAL_HH_INCOME'] = hh_income_ftotinc_both_notnull['FTOTINC']

    hhincome_null_ftotinc_notnull = single_family[(single_family['HHINCOME'].isnull()) & (single_family['FTOTINC'].notnull())]
    print(f"Number of rows where HHINCOME is null and FTOTINC is not null: {len(hhincome_null_ftotinc_notnull)}")
    print("Indices with HHINCOME null and FTOTINC not null:")
    print(hhincome_null_ftotinc_notnull.index)

    df.loc[hhincome_null_ftotinc_notnull.index, 'ACTUAL_HH_INCOME'] = hhincome_null_ftotinc_notnull['FTOTINC']

    ftotinc_null_hhincome_notnull = single_family[(single_family['FTOTINC'].isnull()) & (single_family['HHINCOME'].notnull())]
    print(f"Number of rows where FTOTINC is null and HHINCOME is not null: {len(ftotinc_null_hhincome_notnull)}")
    print("Indices with FTOTINC null and HHINCOME not null:")
    print(ftotinc_null_hhincome_notnull.index)

    df.loc[ftotinc_null_hhincome_notnull.index, 'ACTUAL_HH_INCOME'] = ftotinc_null_hhincome_notnull['HHINCOME']

    hhincome_ftotinc_null_others_notnull = single_family[(single_family[['HHINCOME', 'FTOTINC']].isnull().all(axis=1)) & (single_family[null_income_columns[2:]].notnull().any(axis=1))]
    print(f"Number of rows where HHINCOME and FTOTINC are null, but other income columns are not null: {len(hhincome_ftotinc_null_others_notnull)}")

    return df


def split_multifamily_households(df):
    """
    Split multifamily households into separate entities and adjust household weights.

    This function identifies and splits multifamily households into separate family entities to determine eligibility
    by 'family' rather than the census-defined household. It creates a unique SERIAL NUMBER for each family (named FAMILYNUMBER)
    by combining CBSERIAL (unique household identifier) and FAMUNIT (family unit identifier).

    It also adjusts the household weight (HHWT) by creating a new column REALHHWT. For single-family households, REALHHWT matches HHWT.
    For previously multifamily households, REALHHWT is the original statistical weight (HHWT) divided by the number of families originally
    in the household (NFAMS_B4_SPLIT).

    Parameters:
    ----------
    df : pd.DataFrame
        The input dataframe containing census data.

    Returns:
    -------
    pd.DataFrame
        The updated dataframe with split households and adjusted weights.

    Notes:
    -----
    - This function corrects FAMUNIT for single-family households.
    - The function renames the NFAMS column to NFAMS_B4_SPLIT and creates a new REALHHWT column.

    Verification:
    -------------
    Verified on 2024-06-25 with:
    - test_data_1
    - production_data
    """
    # Correct FAMUNIT for single-family households
    df.loc[(df['NFAMS'] == 1) & df['FAMUNIT'].isin([0, '00', None]), 'FAMUNIT'] = 1

    # Check for problematic FAMUNIT values after correction
    problematic_famunit_after = df[df['FAMUNIT'].isin([0, '00']) | (df['FAMUNIT'] > 60) | df['FAMUNIT'].isnull()]
    print(f"Number of rows with problematic FAMUNIT values after correction: {len(problematic_famunit_after)}")

    # Create FAMILYNUMBER column with unique family number for each family and allocated County
    print('Creating FAMILYNUMBER column...')
    df['FAMILYNUMBER'] = df['CBSERIAL'].astype(str) + df['FAMUNIT'].astype(str) + df['County_Name']


    # Rename NFAMS to NFAMS_B4_SPLIT to keep track of the original number of families
    print('Renaming NFAMS column to NFAMS_B4_SPLIT...')
    df.rename(columns={'NFAMS': 'NFAMS_B4_SPLIT'}, inplace=True)

    # Adjust the REALHHWT column
    print('Creating new column REALHHWT...')
    print('Dividing HHWT by NFAMS_B4_SPLIT for multifamily households...')
    df['REALHHWT'] = df['Allocated_HHWT'] / df['NFAMS_B4_SPLIT']

    return df


def process_multi_family_income_data(df):
    """
    Process and clean income variables for previously multifamily households.

    This function examines and flags anomalous income values for households that were previously
    categorized as multifamily (NFAMS_B4_SPLIT > 1). It fills missing income values by summing
    other available income columns and updates the 'ACTUAL_HH_INCOME' column accordingly.

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing household data.

    Returns:
    -------
    pd.DataFrame
        The updated DataFrame with cleaned income variables for multifamily households.

    Notes:
    -----
    - This function identifies rows with all null income values.
    - It fills the 'ACTUAL_HH_INCOME' column with 'FTOTINC' where available, and sums other income columns where 'FTOTINC' is null.

    Verification:
    -------------
    Verified on 2024-06-25 with:
    - test_data_1
    - production_data
    """
    # Identify rows that were previously multifamily households
    multi_family_rows = df[df['NFAMS_B4_SPLIT'] > 1]
    unique_multi_family_households = multi_family_rows['FAMILYNUMBER'].nunique()
    print(f"Number of previously multifamily household members (rows): {len(multi_family_rows)}")
    print(f"Number of previously multifamily households (number of families): {unique_multi_family_households}")

    # Define income columns to check for null values
    income_columns = [
        'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
        'INCINVST', 'INCRETIR', 'INCSUPP', 'INCOTHER', 'INCEARN'
    ]

    # Identify rows with all null income values
    all_null_income = multi_family_rows[multi_family_rows[income_columns].isnull().all(axis=1)]
    print(f"Number of previously multifamily households with all null income values: {len(all_null_income)}")

    # Fill 'ACTUAL_HH_INCOME' with 'FTOTINC' where 'FTOTINC' is not null
    ftotinc_notnull = multi_family_rows[multi_family_rows['FTOTINC'].notnull()]
    df.loc[ftotinc_notnull.index, 'ACTUAL_HH_INCOME'] = ftotinc_notnull['FTOTINC']
    print(f"Number of previously multifamily households with non-null FTOTINC values: {len(ftotinc_notnull)}")

    # Sum other income columns where 'FTOTINC' is null and store in 'OTHERINCOME_PERSONAL'
    ftotinc_null = multi_family_rows[multi_family_rows['FTOTINC'].isnull()]
    df.loc[ftotinc_null.index, 'OTHERINCOME_PERSONAL'] = ftotinc_null[income_columns[2:]].sum(axis=1)
    other_income_filled_rows = df[df['OTHERINCOME_PERSONAL'].notnull()]
    print(f"Number of rows with a value in OTHERINCOME_PERSONAL: {len(other_income_filled_rows)}")

    # Sum 'OTHERINCOME_PERSONAL' for each unique 'FAMILYNUMBER' and store in 'OTHERINCOME_FAMILY'
    other_income_by_family = other_income_filled_rows.groupby('FAMILYNUMBER')['OTHERINCOME_PERSONAL'].sum()
    df['OTHERINCOME_FAMILY'] = df['FAMILYNUMBER'].map(other_income_by_family)
    other_income_family_filled_rows = df[df['OTHERINCOME_FAMILY'].notnull()]
    print(f"Number of rows with a value in OTHERINCOME_FAMILY: {len(other_income_family_filled_rows)}")

    # Fill 'ACTUAL_HH_INCOME' with 'OTHERINCOME_FAMILY' where 'ACTUAL_HH_INCOME' is null
    rows_to_fill = df[df['OTHERINCOME_FAMILY'].notnull() & df['ACTUAL_HH_INCOME'].isnull()]
    df.loc[rows_to_fill.index, 'ACTUAL_HH_INCOME'] = rows_to_fill['OTHERINCOME_FAMILY']
    print(f"Number of rows filled in ACTUAL_HH_INCOME with OTHERINCOME_FAMILY: {len(rows_to_fill)}")
    print(f"Number of rows that still have empty values in ACTUAL_HH_INCOME: {df['ACTUAL_HH_INCOME'].isnull().sum()}")

    return df