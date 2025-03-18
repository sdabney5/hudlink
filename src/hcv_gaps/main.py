"""
Main script to process Housing Choice Voucher (HCV) eligibility data.

This script executes the following workflow:
1. Load Data
2. Process Counties and Allocation
3. Clean and Split Data
4. Feature Engineering
5. Eligibility Calculation
6. Adjust for Prisoners
7. Generate Final Outputs

The script uses configuration settings from the config.py file.
"""

import logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from config import CONFIG
from hcv_data_loading import (
    load_ipums_data,
    load_crosswalk_data,
    load_income_limits,
    load_incarceration_df,
    load_hud_hcv_data
)
from hcv_fill_counties_and_allocation import fill_missing_county_values
from hcv_income_cleaning_and_household_splitting import (
    clean_single_family_income_data,
    split_multifamily_households,
    process_multi_family_income_data
)
from hcv_family_feature_engineering import family_feature_engineering, flatten_households_to_single_rows
from hcv_eligibility_calculation import calculate_hcv_eligibility
from hcv_prisoner_adjustment import stratified_selection_for_incarcerated_individuals
from hcv_final_outputs import calculate_voucher_gap_and_save

def process_hcv_eligibility(config):
    """
    Main function to process HCV eligibility data.
    Workflow:
    1. Load Data
    2. Process Counties and Allocation
    3. Clean and Split Data
    4. Feature Engineering
    5. Eligibility Calculation
    6. Adjust for Prisoners
    7. Final Outputs
    Parameters:
    config (dict): Configuration dictionary containing paths to data files and processing options.
    """
    # Load Data
    ipums_df = load_ipums_data(config['ipums_data_path'])
    if ipums_df is None:
        logging.error("Error: Failed to load IPUMS data. Exiting script.")
        exit(1)
    logging.info("Loaded IPUMS data")

    crosswalk_2012_df, crosswalk_2022_df = load_crosswalk_data(config['crosswalk_2012_path'], config['crosswalk_2022_path'])
    if crosswalk_2012_df is None or crosswalk_2022_df is None:
        logging.error("Error: Failed to load crosswalk data. Exiting script.")
        exit(1)
    logging.info("Loaded 2012 and 2022 crosswalk data")

    income_limits_df = load_income_limits(config['income_limits_path'])
    if income_limits_df is None:
        logging.error("Error: Failed to load income limits data. Exiting script.")
        exit(1)
    logging.info("Loaded income limits data")
    
    incarceration_df = load_incarceration_df(config['incarceration_data_path'])
    if incarceration_df is None:
        logging.error("Error: Failed to load incarceration data. Exiting script.")
        exit(1)
    logging.info("Loaded incarceration data")
    
    hud_hcv_df = load_hud_hcv_data(config['hud_hcv_data_path'])
    if hud_hcv_df is None:
        logging.error("Error: Failed to load HUD HCV data. Exiting script.")
        exit(1)
    logging.info("Loaded HUD HCV data")
    
    
    # Process Counties and Allocation
    ipums_df = fill_missing_county_values(ipums_df, crosswalk_2012_df, crosswalk_2022_df)
    logging.info("Complete: processed missing county values")
    logging.info(ipums_df.head())
    
    # Clean and Split Data
    ipums_df = clean_single_family_income_data(ipums_df)
    logging.info("Complete: clean single-family income data")
    logging.info(ipums_df.head())

    ipums_df = split_multifamily_households(ipums_df)
    logging.info("Complete: split multifamily households")
    logging.info(ipums_df.head())

    ipums_df = process_multi_family_income_data(ipums_df)
    logging.info("Complete: process multi-family income data")

    # Feature Engineering
    ipums_df = family_feature_engineering(ipums_df)
    logging.info("Complete: perform family feature engineering")

    ipums_df = flatten_households_to_single_rows(ipums_df)
    logging.info("Complete: flatten households to single rows")

    # Eligibility Calculation
    ipums_df = calculate_hcv_eligibility(ipums_df, income_limits_df)
    logging.info("Complete: calculate HCV eligibility")

    # Adjust for Prisoners
    ipums_df = stratified_selection_for_incarcerated_individuals(ipums_df, incarceration_df,
                                                            config['prisoners_identified_by_GQTYPE2'],
                                                            config['race_sampling'],
                                                            config['verbose'])
    logging.info("Complete: adjusted for prisoners")

    # Final Outputs
    calculate_voucher_gap_and_save(ipums_df, hud_hcv_df, config['output_directory'], config['display_race_stats'])

if __name__ == "__main__":
    process_hcv_eligibility(CONFIG)