"""
Adjust eligibility by removing or sampling incarcerated individuals.

This module provides a function to adjust eligibility
by accounting for prisoners in each county. It can directly mark group-quartered
individuals (GQTYPE==2) as ineligible, or perform race-based sampling to remove
households until county prisoner totals are met.

Functions:
    - stratified_selection_for_incarcerated_individuals: Zeroes out eligibility for
      selected households based on incarceration data and options.
"""

import logging
import numpy as np


def stratified_selection_for_incarcerated_individuals(
        eligibility_df,
        incarceration_df=None,
        exclude_group_quarters=False,
        race_sampling=False,
        verbose=False
    ):
    """
    Adjust eligibility by removing/incorporating incarcerated individuals.

    Parameters:
        eligibility_df (pd.DataFrame):
            IPUMS DataFrame with eligibility flags and at least:
            'County_Name', 'GQTYPE', 'FAMSIZE', 'Eligible_at_80%',
            'REALHHWT', 'RACE', and the weighted eligibility columns.

        incarceration_df (pd.DataFrame, optional):
            DataFrame containing county prisoner counts with columns:
            ['County_Name', 'Ttl_Incarc', 'Ttl_White_Incarc', 'Ttl_Minority_Incarc'].
            If None, no adjustment is applied (unless GQTYPE2 is used).

        prisoners_identified_by_GQTYPE2 (bool):
            If True, mark all GQTYPE==2 households as ineligible directly.

        race_sampling (bool):
            If True, perform race-based sampling within each county to match
            Ttl_White_Incarc and Ttl_Minority_Incarc targets. Otherwise, remove
            by total count (Ttl_Incarc).

        verbose (bool):
            If True, log counts removed per county and race.

    Returns:
        pd.DataFrame:
            Updated eligibility DataFrame with incarcerated households set to zero
            for all eligibility columns.
    """
    # Columns to zero out when a household is deemed ineligible
    eligibility_columns = [
        'Eligible_at_30%', 'Eligible_at_50%', 'Eligible_at_80%',
        'Weighted_Eligibility_Count_30%', 'Weighted_Eligibility_Count_50%', 'Weighted_Eligibility_Count_80%',
        'Weighted_White_HH_Eligibility_Count_30%', 'Weighted_White_HH_Eligibility_Count_50%', 'Weighted_White_HH_Eligibility_Count_80%',
        'Weighted_Minority_HH_Eligibility_Count_30%', 'Weighted_Minority_HH_Eligibility_Count_50%', 'Weighted_Minority_HH_Eligibility_Count_80%'
    ]

    # Option 1: Directly mark GQTYPE==2 as ineligible
    if exclude_group_quarters:
        prisoners = eligibility_df[eligibility_df['GQTYPE'] == 2]
        for county, grp in prisoners.groupby('County_Name'):
            eligibility_df.loc[grp.index, eligibility_columns] = 0
            if verbose:
                total_weight = grp['REALHHWT'].sum()
                logging.info(f"County: {county}, Removed Prisoner Weight: {total_weight}")
        if verbose:
            total_removed = prisoners['REALHHWT'].sum()
            logging.info(f"Total prisoners marked ineligible: {total_removed}")
        return eligibility_df

    # Option 2: Use incarceration_df to sample/remove households
    if incarceration_df is None:
        if verbose:
            logging.info("No incarceration data provided; skipping adjustment.")
        return eligibility_df

    # Filter potential inmates: group-quartered (GQTYPE==1), single-family (FAMSIZE==1), eligible at 80%
    potential = eligibility_df[
        (eligibility_df['GQTYPE'] == 1) &
        (eligibility_df['FAMSIZE'] == 1) &
        (eligibility_df['Eligible_at_80%'] == 1)
    ].copy()

    # Use categorical dtype for faster grouping
    potential['County_Name'] = potential['County_Name'].astype('category')
    potential['RACE'] = potential['RACE'].astype('category')

    # Pre-group by county for repeated access
    county_groups = potential.groupby('County_Name')

    def select_inmates_vec(df, target):
        """
        Randomly select rows until cumulative REALHHWT ≈ target.

        Performs one random shuffle and cumulative sum. Chooses the subset whose
        sum is closest to the target.

        Parameters:
            df (pd.DataFrame): Subset of households in one county/race.
            target (float): Total weight to remove.

        Returns:
            Index (list-like): Row indices to mark as removed.
        """
        if df.empty or target <= 0:
            return []

        # Shuffle by random key and compute cumulative sum
        df2 = df.assign(_rand=np.random.rand(len(df))).sort_values('_rand')
        csum = df2['REALHHWT'].cumsum()

        # Mask A: all rows where csum ≤ target
        maskA = csum <= target

        # Mask B: rows up to closest to target
        idx_closest = (csum - target).abs().idxmin()
        maskB = df2.index <= idx_closest

        # Choose which mask yields sum closer to target
        sumA = csum[maskA].sum()
        sumB = csum[maskB].sum()
        best_mask = maskA if abs(sumA - target) < abs(sumB - target) else maskB

        return df2.index[best_mask]

    # Iterate through each county’s incarceration row
    for _, incar in incarceration_df.iterrows():
        county = incar['County_Name']
        if verbose:
            logging.info(
                f"Processing {county}: Total Incarc={incar['Ttl_Incarc']}, "
                f"RaceSampling={race_sampling}"
            )

        try:
            df_cty = county_groups.get_group(county)
        except KeyError:
            if verbose:
                logging.info(f"No potential inmates for county: {county}")
            continue

        if race_sampling:
            # Separate by race
            whites      = df_cty[df_cty['RACE'] == 1]
            minorities  = df_cty[df_cty['RACE'] != 1]

            # Select based on white/minority targets
            sel_w = select_inmates_vec(whites,     incar['Ttl_White_Incarc'])
            sel_m = select_inmates_vec(minorities, incar['Ttl_Minority_Incarc'])

            eligibility_df.loc[sel_w, eligibility_columns] = 0
            eligibility_df.loc[sel_m, eligibility_columns] = 0

            if verbose:
                w_removed = eligibility_df.loc[sel_w, 'REALHHWT'].sum()
                m_removed = eligibility_df.loc[sel_m, 'REALHHWT'].sum()
                logging.info(f"{county}: Removed White weight={w_removed}, Minority weight={m_removed}")
        else:
            # Remove based on total incarcerated count
            sel_all = select_inmates_vec(df_cty, incar['Ttl_Incarc'])
            eligibility_df.loc[sel_all, eligibility_columns] = 0

            if verbose:
                total_removed = eligibility_df.loc[sel_all, 'REALHHWT'].sum()
                logging.info(f"{county}: Removed total weight={total_removed}")

    return eligibility_df
