"""
hudlink Processing Module

This module contains the core function that produces hudink eligibility data for a single state-year combination.
The workflow includes:
  1. Load IPUMS person-level data.
  2. Load crosswalk data.
  3. Load income limits.
  4. Load HUD PSH data.
  5. Fill missing county values.
  6. Clean and split multi-family households.
  7. Engineer household-level flags.
  8. Flatten to one row per household.
  9. Calculate eligibility at 30/50/80% thresholds.
  10. Generate one program-linked summary CSV per HUD program.
  11. Optionally clear the IPUMS API cache.

This script is intended for use by policy researchers and analysts and is designed to be run
as part of a reproducible pipeline.

The function expects a configuration dictionary with file paths and processing options.
"""

import logging
import threading

from .hudlink_data_loading import (
    load_ipums_data,
    load_crosswalk_data,
    load_income_limits,
    load_hud_psh_data
)
from .hudlink_fill_counties_and_allocation import fill_missing_county_values
from .hudlink_income_cleaning_and_household_splitting import (
    clean_single_family_income_data,
    split_multifamily_households,
    process_multi_family_income_data
)
from .hudlink_family_feature_engineering import (
    family_feature_engineering,
    flatten_households_to_single_rows
)
from .hudlink_eligibility_calculation import calculate_eligibility
from .hudlink_final_outputs import calculate_and_save_linked_summaries
from .file_utils import clear_api_downloads
from .ui import show_processing_spinner


def process_eligibility(config: dict) -> None:
    """
    Process eligibility data for a single state-year combination.

    Parameters:
        config (dict): Configuration dictionary containing:
            - 'ipums_data_path'
            - 'crosswalk_2012_path', 'crosswalk_2022_path'
            - 'income_limits_path'
            - 'hud_psh_data_path'
            - 'output_directory'
            - 'state', 'year'
            - 'split_households_into_families' (bool)
            - 'race_sampling' (bool)
            - 'verbose' (bool)
            - 'exclude_group_quarters' (bool)
            - 'program_labels' (list of str)
            - 'api_settings': {
                  'use_ipums_api', 'ipums_api_token',
                  'download_dir', 'clear_api_cache'
              }
    """
    # Start processing spinner
    stop_processing = threading.Event()
    processing_thread = threading.Thread(target=show_processing_spinner, args=(stop_processing,))
    processing_thread.start()    
    
    
    try: 
        # 1. Load IPUMS person-level data
        ipums_df = load_ipums_data(
            config["ipums_data_path"])
        logging.info("Loaded IPUMS data")
    
        # 2. Load crosswalk data
        crosswalk_2012_df, crosswalk_2022_df = load_crosswalk_data(
            config["crosswalk_2012_path"], config["crosswalk_2022_path"]
        )
        logging.info("Loaded crosswalk data")
    
        # 3. Load income limits
        income_limits_df = load_income_limits(
            config["income_limits_path"],
            config["income_limit_agg"],
            config['state'])
        logging.info("Loaded income limits")
    
        # 4. Load HUD PSH data
        hud_psh_df = load_hud_psh_data(config)
        logging.info("Loaded HUD PSH data")
    
        # 5. Fill missing county values in IPUMS
        ipums_df = fill_missing_county_values(
            ipums_df, crosswalk_2012_df, crosswalk_2022_df
        )
        logging.info("Processed missing county values")
    
        # 6. Clean and split multi-family households
        ipums_df = clean_single_family_income_data(ipums_df)
        logging.info("Cleaned single-family income data")
        ipums_df = split_multifamily_households(ipums_df)
        logging.info("Split multifamily households")
        ipums_df = process_multi_family_income_data(ipums_df)
        logging.info("Processed multi-family income data")
    
        # 7. Feature engineering: attach household-level elig_ flags
        ipums_df = family_feature_engineering(ipums_df)
        logging.info("Completed family feature engineering")
    
        # 8. Flatten to one row per household
        ipums_df = flatten_households_to_single_rows(ipums_df)
        logging.info("Flattened households to single rows")
    
        # 9. Calculate eligibility thresholds
        if config.get("split_households_into_families", False):
            weight_col = "Allocated_HHWT"
            weight_suffix = "_FAM"
        else:
            weight_col = "REALHHWT"
            weight_suffix = "_HH"
    
        ipums_df = calculate_eligibility(
            ipums_df,
            income_limits_df,
            weight_col=weight_col,
            exclude_group_quarters=config.get("exclude_group_quarters", False)
        )
        logging.info("Calculated eligibility at 30/50/80% thresholds")
    
        # 10. Final outputs: one linked summary per program label
        calculate_and_save_linked_summaries(
            elig_df=ipums_df,
            hud_psh_df=hud_psh_df,
            program_labels=config["program_labels"],
            output_dir=config["output_directory"],
            state=config["state"],
            year=config["year"],
            weight_suffix=weight_suffix
        )
        logging.info("Saved program-linked summaries")
    
        # 11. Optionally clear IPUMS API cache
        api_cfg = config.get("api_settings", {})
        if api_cfg.get("clear_api_cache", False):
            cache_dir = api_cfg.get("download_dir", "data/api_downloads")
            clear_api_downloads(cache_dir)
            logging.info("Cleared IPUMS API downloads cache")
            
    finally:
        stop_processing.set()
        print("\033[2K\r Data processing completed!")
        processing_thread.join()
