"""
hcv_prisoner_adjustment.py
Adjusts incarcerated persons HCV eligibility

This module contains a function to adjust Housing Choice Voucher (HCV) eligibility by removing incarcerated individuals
based on county prisoner counts and demographics. It provides options to directly identify prisoners using GQTYPE,
and to perform race-based sampling when adjusting eligibility.

Functions:

1. stratified_selection_for_incarcerated_individuals(eligibility_df, incarceration_df=None, prisoners_identified_by_GQTYPE2=False, race_sampling=False, verbose=False):
    Adjusts HCV eligibility of group-quartered individuals based on county prisoner counts and demographics. Optionally
    uses GQTYPE to identify prisoners directly or performs race-based sampling.

Usage:
To use, import this module and call the `stratified_selection_for_incarcerated_individuals` function with the eligibility
dataframe and optionally the incarceration dataframe.

Example:
    import hcv_prisoner_adjustment as hcv_prisoner

    ipums_df = load_ipums_data('path_to_ipums_data.csv')
    incarceration_df = load_incarceration_data('path_to_incarceration_data.csv')

    adjusted_ipums_df = hcv_prisoner.stratified_selection_for_incarcerated_individuals(ipums_df, incarceration_df)
"""

import logging

logging.info("This is a log message from hcv_prisoner_adjustment.py")

def stratified_selection_for_incarcerated_individuals(eligibility_df, incarceration_df=None,
                                                      prisoners_identified_by_GQTYPE2=False, race_sampling=False, verbose=False):
    """
    Adjust eligibility of group-quartered individuals based on county prisoner counts and demographics.

    This function adjusts HCV eligibility by removing incarcerated individuals from the eligibility list based on
    county prisoner counts and demographics. It can use GQTYPE to identify prisoners directly, and it supports
    race-based sampling to adjust the eligibility counts.

    Parameters:
    ----------
    eligibility_df : pd.DataFrame
        The IPUMS dataframe with eligibility determinations calculated.
    incarceration_df : pd.DataFrame, optional
        The incarceration dataset containing prisoner counts and race percentages for each county.
    prisoners_identified_by_GQTYPE2 : bool
        If True, use GQTYPE == 2 to identify prisoners directly.
    race_sampling : bool
        If True, perform race-based sampling; if False, just remove by county count.
    verbose : bool
        If True, print the count of removed individuals for each county and race group.

    Returns:
    -------
    pd.DataFrame
        The updated eligibility dataframe with adjusted eligibility status for incarcerated individuals.

    Notes:
    -----
    - When `prisoners_identified_by_GQTYPE2` is True, the function directly marks individuals with GQTYPE == 2 as ineligible.
    - When `race_sampling` is True, the function performs race-based sampling to adjust the eligibility counts by race.
    - Prints detailed information if `verbose` is True, helping to track the adjustment process.
    """

    eligibility_columns = ['Eligible_at_30%', 'Eligible_at_50%', 'Eligible_at_80%',
                           'Weighted_Eligibility_Count_30%', 'Weighted_Eligibility_Count_50%', 'Weighted_Eligibility_Count_80%',
                           'Weighted_White_HH_Eligibility_Count_30%', 'Weighted_White_HH_Eligibility_Count_50%', 'Weighted_White_HH_Eligibility_Count_80%',
                           'Weighted_Minority_HH_Eligibility_Count_30%', 'Weighted_Minority_HH_Eligibility_Count_50%', 'Weighted_Minority_HH_Eligibility_Count_80%']

    if prisoners_identified_by_GQTYPE2:
        prisoners_df = eligibility_df[eligibility_df['GQTYPE'] == 2]
        for county_name, county_group in prisoners_df.groupby('County_Name_state_abbr'):
            prisoners_count = county_group['REALHHWT'].sum()
            eligibility_df.loc[county_group.index, eligibility_columns] = 0
            if verbose:
                logging.info(f"County: {county_name}, Removed Prisoner Count: {prisoners_count}")

        total_prisoners_removed = prisoners_df['REALHHWT'].sum()
        if verbose:
            logging.info(f"Total Prisoners Marked Ineligible: {total_prisoners_removed}")
        return eligibility_df

    if incarceration_df is None:
        if verbose:
            logging.info("No incarceration data provided, returning eligibility_df unchanged.")
        return eligibility_df

    potential_inmates = eligibility_df[
        (eligibility_df['GQTYPE'] == 1) &
        (eligibility_df['FAMSIZE'] == 1) &
        (eligibility_df['Eligible_at_80%'] == 1)
    ]

    if verbose:
        logging.info("Potential inmates dataframe:")
        logging.info(potential_inmates.head())

    def select_inmates(target_count, inmates):
        selected_count = 0
        selected_indices = []
        while selected_count < target_count:
            if inmates.empty:
                break
            selected_row = inmates.sample(n=1)
            selected_indices.append(selected_row.index[0])
            selected_count += selected_row['REALHHWT'].values[0]
            inmates = inmates.drop(selected_row.index)
            if selected_count >= target_count or abs(selected_count - target_count) <= 5:
                break
        return selected_indices

    for _, incar_row in incarceration_df.iterrows():
        county_name = incar_row['County_Name']
        total_incarc = incar_row['Ttl_Incarc']

        if verbose:
            logging.info(f"Processing county: {county_name}, Total Incarcerated: {total_incarc}, Race Sampling: {race_sampling}")

        county_inmates = potential_inmates[potential_inmates['County_Name_state_abbr'] == county_name]
        if verbose and county_inmates.empty:
            logging.info(f"No potential inmates found for county: {county_name}")

        if race_sampling:
            total_white_incarc = incar_row['Ttl_White_Incarc']
            total_minority_incarc = incar_row['Ttl_Minority_Incarc']

            white_inmates = county_inmates[county_inmates['RACE'] == 1]
            minority_inmates = county_inmates[county_inmates['RACE'] != 1]

            selected_white_indices = select_inmates(total_white_incarc, white_inmates)
            selected_minority_indices = select_inmates(total_minority_incarc, minority_inmates)

            eligibility_df.loc[selected_white_indices, eligibility_columns] = 0
            eligibility_df.loc[selected_minority_indices, eligibility_columns] = 0

            if verbose:
                white_removed_count = sum(eligibility_df.loc[selected_white_indices, 'REALHHWT'])
                minority_removed_count = sum(eligibility_df.loc[selected_minority_indices, 'REALHHWT'])
                logging.info(f"County: {county_name}, Adjusted White REALHHWT: {white_removed_count}")
                logging.info(f"County: {county_name}, Adjusted Minority REALHHWT: {minority_removed_count}")
        else:
            selected_indices = select_inmates(total_incarc, county_inmates)

            if verbose and len(selected_indices) == 0:
                logging.info(f"No inmates selected for county: {county_name}, Total Incarcerated: {total_incarc}")

            eligibility_df.loc[selected_indices, eligibility_columns] = 0

            if verbose:
                removed_count = sum(eligibility_df.loc[selected_indices, 'REALHHWT'])
                logging.info(f"County: {county_name}, Adjusted Total REALHHWT: {removed_count}")

    return eligibility_df
