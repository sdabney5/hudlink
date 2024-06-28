"""
hcv_family_feature_engineering.py
Engineers family/household level features in the IPUMS dataset.

This module contains functions for engineering family-level features and condensing households
into single rows within the IPUMS dataset.

Functions:

1. family_feature_engineering(df):
    Adds family-level features to the dataset, including education metrics and race binary columns.

2. flatten_households_to_single_rows(df):
    Condenses the DataFrame to one representative row per family, aggregating specified columns and
    notifying the user of any extra columns.

Usage:
To use, import this module and call the functions with the IPUMS dataframe as the argument.
The functions will return the modified DataFrame with engineered family features and condensed households.

Example:
    import hcv_family_feature_engineering as hcv_engineering

    ipums_df = hcv_engineering.family_feature_engineering(ipums_df)
    ipums_df = hcv_engineering.flatten_households_to_single_rows(ipums_df)
"""

#imports
import pandas as pd


def family_feature_engineering(df):
    """
    Add family-level features to the dataset, including education metrics and race binary columns.

    This function processes census data to add representative family-level features, including education metrics
    and race binary columns. It categorizes family-level race based on the race of the head of household,
    consistent with HUD's method in HCV reports.

    The function aggregates individual-level data to create family-level features while preserving the original
    individual records. It also creates a new variable, REALHHWT. For single-family households, REALHHWT matches
    HHWT. For previously multifamily households, REALHHWT is the original statistical weight (HHWT) divided by
    the number of families originally in the household (NFAMS_B4_SPLIT).

    Parameters:
    ----------
    df : pd.DataFrame
        The input DataFrame containing individual-level census data.

    Returns:
    -------
    pd.DataFrame
        The updated DataFrame with added family-level features and adjusted household weights.

    Notes:
    -----
    - This function assumes the DataFrame includes columns for family identification (FAMILYNUMBER),
      relationship to head of household (RELATE), race (RACE), and various education and income variables.
    """
    # Helper function to categorize race based on head of household
    def categorize_race_by_head(relate_codes, race_codes):
        race = None
        if 1 in relate_codes:
            race = race_codes[relate_codes.index(1)]
        elif 2 in relate_codes:
            race = race_codes[relate_codes.index(2)]
        else:
            race = race_codes[0]

        if race == 1:
            return "White"
        elif race == 2:
            return "Black"
        elif race == 3:
            return "Other"
        elif race in {4, 5, 6}:
            return "Asian"
        elif race in {7, 8, 9}:
            return "Mixed Race"
        else:
            return "Other_Race"

    # Education categorization function
    def categorize_education(educ_codes):
        if educ_codes.max() in range(2, 63):
            return "High School or Below"
        elif educ_codes.max() in range(63, 101):
            return "Some College"
        elif educ_codes.max() == 101:
            return "Bachelor's Degree"
        elif educ_codes.max() in range(102, 117):
            return "Master's & Above"
        else:
            return "No Schooling"

    # Dictionary for groupby aggregation
    aggregation = {
        'AGE': [
            ('SENIOR_HOUSEHOLD', lambda x: 1 if (x > 64).any() else 0),
            ('NUM_CHILDREN', lambda x: (x < 18).sum())
        ],
        'VETSTAT': [('VET_HOUSEHOLD', lambda x: 1 if (x == 2).any() else 0)],
        'EDUCD': [
            ('HIGHEST_EDUC', categorize_education),
            ('HS_COMPLETE', lambda x: 1 if (x >= 62).any() else 0),
            ('BACHELOR_COMPLETE', lambda x: 1 if x.eq(101).any() else 0),
            ('GRAD_SCHOOL', lambda x: 1 if (x > 101).any() else 0),
            ('TWO_COLLEGE_GRADS', lambda x: 1 if x[x.eq(101)].count() >= 2 else 0)
        ],
        'HHTYPE': [
            ('MARRIED_FAMILY_HH', lambda x: 1 if (x == 1).any() else 0),
            ('SINGLE_PARENT_HH', lambda x: 1 if (x == 2).any() or (x == 3).any() else 0)
        ],
        'EMPSTAT': [('EMPLOYED', lambda x: 1 if (x == 1).any() else 0)],
        'RACE': [('HOUSEHOLD_RACE', lambda x: categorize_race_by_head(x.tolist(), x.tolist()))],
        'RELATE': [('RELATE_CODES', lambda x: x.tolist())]
    }

    # Perform a single groupby operation
    print('Aggregating Family Features....')
    family_features = df.groupby('FAMILYNUMBER').agg(aggregation)

    # Flatten the multi-index columns
    family_features.columns = [col[1] for col in family_features.columns.values]

    # Add binary columns for each race category
    family_features['White_HH'] = family_features['HOUSEHOLD_RACE'] == 'White'
    family_features['Black_HH'] = family_features['HOUSEHOLD_RACE'] == 'Black'
    family_features['Asian_HH'] = family_features['HOUSEHOLD_RACE'] == 'Asian'
    family_features['Mixed_Race_HH'] = family_features['HOUSEHOLD_RACE'] == 'Mixed Race'
    family_features['Other_Race_HH'] = family_features['HOUSEHOLD_RACE'] == 'Other_Race'

    # Drop the RELATE_CODES column that used for categorization
    family_features.drop(columns=['RELATE_CODES'], inplace=True)

    # Merge the aggregated features back to the main df
    print('Merging aggregated features back to main df')
    df = df.merge(family_features, on='FAMILYNUMBER', how='left')

    return df

#Function to condense families/households to a single row
def flatten_households_to_single_rows(df):
    """
    Condense the dataframe so there's only one representative row per family.

    This function condenses the DataFrame so there's only one representative row per family. It drops specified
    columns and retains unspecified columns. It aggregates certain columns by taking the first value for each
    family, sums specified columns, and retains the first value for unspecified columns. If the DataFrame contains
    additional columns not specified in the function, it takes the first value for these columns and notifies the user.

    Parameters:
    ----------
    df : pd.DataFrame
        The input dataframe.

    Returns:
    -------
    pd.DataFrame
        The condensed dataframe with one row per family.

    Notes:
    -----
    - The function drops columns that are not needed for the analysis.
    - The function aggregates certain columns by taking the first value for each family.
    - For specified columns that require summation, the function aggregates them by summing.
    - For columns that are not specifically listed, the function retains them and applies the 'first' aggregation.
    - If the DataFrame contains additional columns not specified in the function, the function will take the first value
      for these columns and notify the user.

    Verification:
    -------------
    Verified on 2024-06-25 with:
    - test_data_1
    - production_data
    """
    # Columns to drop
    cols_to_drop = ['OTHERINCOME_FAMILY', 'OTHERINCOME_PERSONAL', 'HHINCOME', 'QOWNERSH', 'QRENTGRS', 'QHHINCOME',
                    'PERNUM', 'PERWT', 'FAMUNIT', 'AGE', 'MARST', 'BIRTHYR', 'HCOVANY', 'SCHOOL', 'EDUC', 'EDUCD',
                    'GRADEATT', 'GRADEATTD', 'SCHLTYPE', 'RELATE', 'RELATED', 'GCRESPON', 'QAGE', 'QMARST',
                    'QSEX', 'QHINSEMP', 'QHINSPUR', 'QHINSTRI', 'QHINSCAI', 'QHINSCAR', 'QHINSVA', 'QHINSIHS',
                    'QEDUC', 'QGRADEAT', 'QSCHOOL', 'QMIGRAT1', 'QMOVEDIN', 'QVETSTAT', 'QTRANTIM', 'QGCRESPO',
                    'INCWAGE', 'INCSS', 'INCWELFR', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCOTHER', 'INCEARN',
                    'VETSTAT', 'VETSTATD', 'FTOTINC']

    # Drop the columns
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # The columns where we'll just take the first value since they should all be the same for a family
    cols_first_value = ['County_Name', 'YEAR', 'HHWT', 'MULTYEAR', 'SAMPLE', 'SERIAL', 'CBSERIAL', 'CBHHTYPE', 'CLUSTER',
                        'REGION', 'STATEICP', 'COUNTYICP', 'COUNTYFIP', 'METRO', 'MET2013', 'MET2013ERR',
                        'CITY', 'PUMA', 'STRATA', 'GQ', 'GQTYPE', 'GQTYPED', 'OWNERSHP', 'OWNERSHPD',
                        'MORTGAGE', 'MORTAMT1', 'RENTGRS', 'FAMILYNUMBER', 'ACTUAL_HH_INCOME', 'NFAMS_B4_SPLIT',
                        'HHTYPE', 'FOODSTMP', 'VEHICLES', 'NMOTHERS', 'NFATHERS', 'MULTGEN',
                        'MULTGEND', 'FAMSIZE', 'POVERTY', 'SENIOR_HOUSEHOLD', 'NUM_CHILDREN', 'VET_HOUSEHOLD',
                        'HIGHEST_EDUC', 'MARRIED_FAMILY HH', 'SINGLE_PARENT HH', 'REALHHWT', 'EMPLOYED', 'CITIZEN',
                        'HISPAN', 'HISPAND', 'RACE', 'RACED', 'White', 'Black', 'Asian', 'Mixed Race',
                        'Other_Race', 'HOUSEHOLD_RACE', 'HS_COMPLETE', 'BACHELOR_COMPLETE',
                        'GRAD_SCHOOL', 'TWO_COLLEGE_GRADS', 'SEX', 'MCDC_PUMA_COUNTY_NAMES', 'Multi_County_Flag',
                        'Black_HH', 'MARRIED_FAMILY_HH', 'Asian_HH', 'Mixed_Race_HH', 'EMPSTAT', 'Other_Race_HH',
                        'SINGLE_PARENT_HH', 'White_HH']

    # Columns where we'll take the sum value
    cols_sum_value = ['UHRSWORK']

    # Group by FAMILYNUMBER and aggregate
    aggregation = {col: 'first' for col in cols_first_value if col in df.columns}
    aggregation.update({col: 'sum' for col in cols_sum_value if col in df.columns})

    # Capture extra columns not specified
    all_columns = set(df.columns)
    specified_columns = set(cols_first_value + cols_sum_value)
    extra_columns = all_columns - specified_columns

    # Add extra columns to the aggregation dictionary with 'first'
    for col in extra_columns:
        aggregation[col] = 'first'

    # Print message if there are extra columns
    if extra_columns:
        print("FYI: The following extra columns were found and their first values were taken for each household:")
        print(", ".join(extra_columns))

    # Group, aggregate, then put FAMILYNUMBER back as a column and reset the index
    condensed_df = df.groupby('FAMILYNUMBER').agg(aggregation)
    condensed_df['FAMILYNUMBER'] = condensed_df.index
    condensed_df.reset_index(drop=True, inplace=True)

    return condensed_df