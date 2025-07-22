"""
hudlink_family_feature_engineering.py

Engineer household-level eligibility flags and flatten to one row per FAMILYNUMBER.

Functions:
    - family_feature_engineering: Attach a broad set of binary elig_ flags to person-level rows.
    - flatten_households_to_single_rows: Collapse to one household row, aggregating flags and core fields.
"""

import logging
import pandas as pd


def family_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Attach household-level eligibility flags (prefixed 'elig_') to each person record.

    Flags cover:
      - Family structure: elig_2adults, elig_1adult,
        elig_female_head, elig_female_head_child,
        elig_male_head, elig_male_head_child
      - Race/ethnicity: elig_minority, elig_white_nonhsp,
        elig_black_nonhsp, elig_native_american_nonhsp,
        elig_asian_nonhsp, elig_mixed_nonhsp,
        elig_otherrace, elig_hispanic
      - Citizenship & tenure: elig_noncitizen,
        elig_owner, elig_renter, elig_mortgage_paid
      - Veteran status: elig_veteran
      - Disability: elig_disab_hearing_vision,
        elig_disab_ambulatory, elig_disab_cognitative,
        elig_disab_independent_living, elig_disab_any
      - Age: elig_age62plus, elig_age75plus
      - Education: elig_hs_complete,
        elig_bachelor_complete, elig_grad_school
      - Employment: elig_employed

    Parameters:
        df: Person-level IPUMS DataFrame with columns including:
            FAMILYNUMBER, RELATE, AGE, SEX, RACE, HISPAN, MARST, NCHILD,
            CITIZEN, OWNERSHP, MORTGAGE, VETSTAT,
            DIFFSENS, DIFFPHYS, DIFFREM, DIFFMOB,
            EDUCD, EMPSTAT.

    Returns:
        pd.DataFrame: Input DataFrame with 'elig_' flags merged back onto each row.
    """
    # Guard required inputs
    required_cols = {
        'FAMILYNUMBER', 'RELATE', 'AGE', 'SEX', 'RACE', 'HISPAN',
        'MARST', 'NCHILD', 'CITIZEN', 'OWNERSHP', 'MORTGAGE',
        'VETSTAT', 'DIFFSENS', 'DIFFPHYS', 'DIFFREM', 'DIFFMOB',
        'EDUCD', 'EMPSTAT'
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns for family_feature_engineering: {missing}")

    # 1) Person-level indicators for any-member flags
    df['_IS_DISAB_HEARING_VISION']   = (df['DIFFSENS'] == 2).astype('uint8')
    df['_IS_DISAB_AMBULATORY']       = (df['DIFFPHYS'] == 2).astype('uint8')
    df['_IS_DISAB_COGNITIVE']        = (df['DIFFREM'] == 2).astype('uint8')
    df['_IS_DISAB_INDEP_LIVING']     = (df['DIFFMOB'] == 2).astype('uint8')
    df['_IS_VET']                    = (df['VETSTAT'] == 2).astype('uint8')

    # Education & employment helpers
    df['_EDU_HS_PLUS']    = (df['EDUCD'] >= 62).astype('uint8')
    df['_EDU_BACHELOR']   = (df['EDUCD'] == 101).astype('uint8')
    df['_EDU_GRAD']       = (df['EDUCD'] > 101).astype('uint8')
    df['_EMPLOYED']       = (df['EMPSTAT'] == 1).astype('uint8')

    # 2) Identify head-of-household: RELATE==1, then spouse, else first
    priority = df['RELATE'].replace({1: 0, 2: 1}).fillna(2)
    rep_idx  = priority.groupby(df['FAMILYNUMBER'], sort=False).idxmin()
    rep = (
        df.loc[rep_idx, [
            'FAMILYNUMBER', 'RELATE', 'AGE', 'SEX',
            'RACE', 'HISPAN', 'MARST', 'NCHILD',
            'CITIZEN', 'OWNERSHP', 'MORTGAGE'
        ]]
        .set_index('FAMILYNUMBER')
    )

    # 3) Head-of-household flags
    rep['elig_2adults']    = ((rep['MARST'] == 1) & (rep['NCHILD'] > 0)).astype('uint8')
    rep['elig_1adult']     = ((rep['MARST'] != 1) & (rep['NCHILD'] > 0)).astype('uint8')
    rep['elig_female_head']       = ((rep['RELATE'] == 1) & (rep['SEX'] == 2)).astype('uint8')
    rep['elig_female_head_child'] = (rep['elig_female_head'] & (rep['NCHILD'] > 0)).astype('uint8')
    rep['elig_male_head']         = ((rep['RELATE'] == 1) & (rep['SEX'] == 1)).astype('uint8')
    rep['elig_male_head_child']   = (rep['elig_male_head'] & (rep['NCHILD'] > 0)).astype('uint8')
    rep['elig_age62plus']         = ((rep['RELATE'] == 1) & (rep['AGE'] > 62)).astype('uint8')
    rep['elig_age75plus']         = ((rep['RELATE'] == 1) & (rep['AGE'] > 74)).astype('uint8')

    # Race/Ethnicity
    rep['elig_minority']               = ((rep['HISPAN'] == 1) | (rep['RACE'] != 1)).astype('uint8')
    rep['elig_white_nonhsp']           = ((rep['HISPAN'] == 0) & (rep['RACE'] == 1)).astype('uint8')
    rep['elig_black_nonhsp']           = ((rep['HISPAN'] == 0) & (rep['RACE'] == 2)).astype('uint8')
    rep['elig_native_american_nonhsp'] = ((rep['HISPAN'] == 0) & (rep['RACE'] == 3)).astype('uint8')
    rep['elig_asian_nonhsp']           = ((rep['HISPAN'] == 0) & rep['RACE'].isin([4,5,6])).astype('uint8')
    rep['elig_mixed_nonhsp']           = ((rep['HISPAN'] == 0) & rep['RACE'].isin([8,9])).astype('uint8')
    rep['elig_otherrace']              = ((rep['HISPAN'] == 0) & (rep['RACE'] == 7)).astype('uint8')
    rep['elig_hispanic']               = (rep['HISPAN'] == 1).astype('uint8')

    # Citizenship & tenure
    rep['elig_noncitizen']    = (rep['CITIZEN'] == 3).astype('uint8')
    rep['elig_owner']         = (rep['OWNERSHP'] == 1).astype('uint8')
    rep['elig_renter']        = rep['OWNERSHP'].isin([0,2]).astype('uint8')
    rep['elig_mortgage_paid'] = (rep['MORTGAGE'] == 1).astype('uint8')

    # drop raw head columns
    rep.drop(columns=[
        'RELATE','AGE','SEX','RACE','HISPAN',
        'MARST','NCHILD','CITIZEN','OWNERSHP','MORTGAGE'
    ], inplace=True)

    # 4) Aggregate any-member and edu/employment flags to household level
    fam = df.groupby('FAMILYNUMBER', sort=False).agg(
        elig_disab_hearing_vision     = ('_IS_DISAB_HEARING_VISION','max'),
        elig_disab_ambulatory         = ('_IS_DISAB_AMBULATORY','max'),
        elig_disab_cognitative        = ('_IS_DISAB_COGNITIVE','max'),
        elig_disab_independent_living = ('_IS_DISAB_INDEP_LIVING','max'),
        elig_veteran                  = ('_IS_VET','max'),
        elig_hs_complete              = ('_EDU_HS_PLUS','max'),
        elig_bachelor_complete        = ('_EDU_BACHELOR','max'),
        elig_grad_school              = ('_EDU_GRAD','max'),
        elig_employed                 = ('_EMPLOYED','max'),
    )

    # disability-any flag
    fam['elig_disab_any'] = fam[[
        'elig_disab_hearing_vision',
        'elig_disab_ambulatory',
        'elig_disab_cognitative',
        'elig_disab_independent_living'
    ]].max(axis=1).astype('uint8')

    # 5) Merge head & fam flags back onto person-level rows
    df = (
        df
        .merge(rep.reset_index(), on='FAMILYNUMBER', how='left')
        .merge(fam.reset_index(), on='FAMILYNUMBER', how='left')
    )
    logging.info("Merged household flags onto %d person rows", len(df))

    # 6) Clean up temporary helper columns
    df.drop(columns=[c for c in df.columns if c.startswith('_')], inplace=True)
    return df


def flatten_households_to_single_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse person-level DataFrame into one row per FAMILYNUMBER.

    - Static fields (IDs, geography, income) use first().
    - Binary elig_ flags use max() to capture any member’s flag.
    - Numeric fields listed in sum_vars (default ['UHRSWORK']) use sum().
    - Any other columns default to first().

    Parameters:
        df (pd.DataFrame): Person-level DataFrame with elig_ flags and core fields.

    Returns:
        pd.DataFrame: One row per FAMILYNUMBER, with aggregated fields.
    """
    # 1) Drop person-only temp columns
    drop_cols = [
        'OTHERINCOME_FAMILY','OTHERINCOME_PERSONAL','HHINCOME','QOWNERSH',
        'QRENTGRS','QHHINCOME','PERNUM','PERWT','FAMUNIT','AGE','MARST',
        'BIRTHYR','HCOVANY','SCHOOL','EDUC','EDUCD','GRADEATT','GRADEATTD',
        'SCHLTYPE','RELATE','RELATED','GCRESPON','QAGE','QMARST','QSEX',
        'QHINSEMP','QHINSPUR','QHINSTRI','QHINSCAR','QHINSVA','QHINSIHS',
        'QEDUC','QGRADEAT','QSCHOOL','QMIGRAT1','QMOVEDIN','QVETSTAT',
        'QTRANTIM','QGCRESPO','INCWAGE','INCSS','INCWELFR','INCINVST',
        'INCRETIR','INCSUPP','INCOTHER','INCEARN','VETSTAT','VETSTATD','FTOTINC'
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # 2) Define aggregation categories
    core_fields = [
        'County_Name','County_Name_Alt','YEAR','STATEICP','COUNTYICP',
        'COUNTYFIP','PUMA','CBHHTYPE','SERIAL','CBSERIAL','CLUSTER',
        'REGION','METRO','FAMSIZE','ACTUAL_HH_INCOME','POVERTY',
        'HHTYPE','REALHHWT','Allocated_HHWT','HHWT','MULTYEAR',
        'SAMPLE','STRATA','GQ','GQTYPE','GQTYPED'
    ]
    static_cols = [c for c in core_fields if c in df.columns]
    elig_flags   = [c for c in df.columns if c.startswith('elig_')]

    # 3) Extendable sum_vars list
    sum_vars   = ['UHRSWORK']
    sum_fields = [c for c in sum_vars if c in df.columns]

    # 4) Build aggregation map
    agg_map = {
        **{c: 'first' for c in static_cols},
        **{c: 'max'   for c in elig_flags},
        **{c: 'sum'   for c in sum_fields}
    }

    # 5) Catch extra columns via first()
    extras = set(df.columns) - set(static_cols) - set(elig_flags) - set(sum_fields) - {'FAMILYNUMBER'}
    if extras:
        logging.info("Flatten: first() on extra columns")
        agg_map.update({c: 'first' for c in extras})

    # 6) Group and aggregate
    condensed = df.groupby('FAMILYNUMBER').agg(agg_map).reset_index()

    # 7) Sanity check
    assert condensed['FAMILYNUMBER'].is_unique, "Duplicate FAMILYNUMBER after flatten"

    return condensed
