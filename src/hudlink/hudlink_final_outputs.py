"""
hudlink_final_outputs.py

Save flattened eligibility and generate PSH‐program‐linked county summaries,
including weighted counts and shares for every elig_ flag at each AMI threshold,
and preserving all HUD PSH columns.
"""

import os
import re
import logging
import pandas as pd

from .file_utils import(
    clean_eligibility_df, 
    tidy_summary_df, 
    clean_up_eligibility_df, 
    add_fips_codes_to_df
    )

# AMI thresholds to process
THRESHOLDS = ["30%", "50%", "80%"]


def save_flat_eligibility_df(
    elig_df: pd.DataFrame,
    output_dir: str,
    state: str,
    year: int | str,
    weight_suffix: str = ""
):
    """
    Clean and save the household‐level eligibility DataFrame.
    """
    df_clean = clean_eligibility_df(elig_df, state, year, warning=True)
    df_clean= add_fips_codes_to_df(df_clean, state)
    df_even_cleaner = clean_up_eligibility_df(df_clean)
    fname = f"{state}_{year}_eligibility{weight_suffix}.csv"
    path = os.path.join(output_dir, fname)
    df_even_cleaner.to_csv(path, index=False)
    logging.info("Saved flat eligibility to %s", path)


def calculate_and_save_linked_summaries(
    elig_df: pd.DataFrame,
    hud_psh_df: pd.DataFrame,
    program_labels: list[str],
    output_dir: str,
    state: str,
    year: int | str,
    weight_suffix: str = ""
):
    """
    For each PSH program_label:
      - Build county summary with weighted counts & shares for each elig_ flag
      - Merge all HUD columns for that program
      - Compute program-specific gap and allocation rate
      - Save one linked CSV per program
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1) Save the flat household‐level eligibility table
    save_flat_eligibility_df(elig_df, output_dir, state, year, weight_suffix)
    
    #1 a) Clean again
    elig_df = clean_eligibility_df(elig_df, state, year)

    # 2) Build county summary (weighted totals + weighted flag counts + shares)
    flags = [c for c in elig_df.columns if c.startswith("elig_")]
    summary = pd.DataFrame({"County_Name": elig_df["County_Name"].unique()}) \
                .set_index("County_Name")

    # Weighted eligibility totals
    for pct in THRESHOLDS:
        wcol = f"Weighted_Eligibility_Count_{pct}"
        summary[wcol] = elig_df.groupby("County_Name")[wcol].sum()

    # Gather all the weighted-flag counts & shares
    new_cols: dict[str, pd.Series] = {}
    for pct in THRESHOLDS:
        wcol = f"Weighted_Eligibility_Count_{pct}"
        # pre-group the totals for this pct
        for flag in flags:
            wflag = f"Weighted_{flag}_Count_{pct}"
            share = f"% Eligible {flag} at {pct}"

            # sum of weight * flag
            sc = (elig_df[flag] * elig_df[wcol]).groupby(elig_df["County_Name"]).sum()
            new_cols[wflag] = sc

            # share = sc / total * 100
            new_cols[share] = sc.div(summary[wcol]).mul(100)

    # Concatenate all new columns
    summary = pd.concat([summary, pd.DataFrame(new_cols)], axis=1).reset_index()

    # prepare normalized name for merge
    summary["County_Name_Normalized"] = (
        summary["County_Name"]
        .str.lower().str.strip()
        .str.replace(r"[.'’]", "", regex=True)
    )

    # 3) Loop over each requested program_label
    for prog in program_labels:
        hud_sub = hud_psh_df[hud_psh_df["program_label"] == prog].copy()
        if hud_sub.empty:
            logging.warning("No HUD records for program_label '%s'; skipping output.", prog)
            continue

        # normalize for merge
        hud_sub["County_Name_Normalized"] = (
            hud_sub["name"]
            .str.lower().str.strip()
            .str.replace(r"[.'’]", "", regex=True)
        )

        # merge in all HUD columns
        merged = summary.merge(
            hud_sub,
            on="County_Name_Normalized",
            how="left"
        ).drop(columns=["County_Name_Normalized"])

        # sanitize program label for column names and filenames
        prog_safe = re.sub(r"\W+", "_", prog.strip().lower())

        # 4) Compute gap & allocation rate for each threshold,
        # preserving negative codes in total_units
        for pct in THRESHOLDS:
            total_w = f"Weighted_Eligibility_Count_{pct}"
            gap_col = f"{prog_safe}_gap_{pct}"
            rate_col = f"{prog_safe}_allocation_rate_{pct}"

            # default to retaining negative total_units code
            merged[gap_col] = merged["total_units"].astype('float64')
            merged[rate_col] = merged["total_units"].astype('float64')

            # only compute for valid (non-negative) total_units
            valid = merged["total_units"] >= 0
            # gap = weighted total - total_units
            merged.loc[valid, gap_col] = (
                merged.loc[valid, total_w] - merged.loc[valid, "total_units"]
            )
            # rate = total_units / weighted total
            denom = merged.loc[valid, total_w].replace({0: pd.NA})
            
            rate_calculation = merged.loc[valid, "total_units"] / denom * 100
            rate_values = pd.to_numeric(rate_calculation, errors='coerce')
            merged.loc[valid, rate_col] = rate_values
            

        # 5) Finalize and save
        linked = tidy_summary_df(merged, state)
        linked = add_fips_codes_to_df(linked, state)
        fname = f"{state}_{year}_{prog_safe}_linked_summary{weight_suffix}.csv"
        path = os.path.join(output_dir, fname)
        linked.to_csv(path, index=False)
        logging.info("Saved linked summary for '%s' to %s", prog, path)
