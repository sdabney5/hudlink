"""
State Processor Module for HCV Eligibility Analysis.

This module processes multiple states and years using the global configuration.
For each state-year combination, it:
  1. Updates the configuration with state-specific file paths using template strings (except for HUD HCV, which is year-specific).
  2. Sets the current state and year in the configuration.
  3. Creates the output directory structure for final analysis outputs.
  4. Checks for and/or downloads the IPUMS data file into a dedicated subdirectory within the data directory.
  5. Updates the configuration's "ipums_data_path" with the downloaded file path.
  6. Updates the HUD HCV data path using the current year.
  7. Calls the core processing function (process_hcv_eligibility) with the updated configuration.
"""

import os
import copy
import logging
from .hcv_processing import process_hcv_eligibility
from .file_utils import create_output_structure
from .api_calls import fetch_ipums_data_api

def update_config_for_state(config, state):
    """
    Update the configuration dictionary for a specific state.
    
    This function takes the global configuration and a state abbreviation,
    and returns a new configuration dictionary with state-specific file paths updated
    using the template strings defined in the global config. (The HUD HCV data path
    is not updated here because it is year-specific and will be updated later.)
    
    Parameters:
        config (dict): The global configuration dictionary.
        state (str): The state abbreviation (expected to match directory names).
        
    Returns:
        dict: A new configuration dictionary with updated file paths for the given state.
    """
    state_config = copy.deepcopy(config)
    state_config["crosswalk_2012_path"] = config["crosswalk_2012_template"].format(
        data_dir=config["data_dir"], state=state)
    state_config["crosswalk_2022_path"] = config["crosswalk_2022_template"].format(
        data_dir=config["data_dir"], state=state)
    state_config["income_limits_path"] = config["income_limits_template"].format(
        data_dir=config["data_dir"], state=state)
    state_config["incarceration_data_path"] = config["incarceration_template"].format(
        data_dir=config["data_dir"], state=state)
    # Do not update hud_hcv_data_path here because it is year-specific.
    return state_config

import os
import logging
import zipfile  # in case you need to handle zipped files
import pandas as pd
from .api_calls import fetch_ipums_data_api

def get_ipums_data_file(config):
    """
    Check if the IPUMS data file for the current state and year exists.
    If it does not, force the API function to download the data into a dedicated
    subdirectory with a recognizable file name.
    
    The file is stored under:
      <data_dir>/api_downloads/<STATE>/ipums_api_downloads/<STATE>_ipums_<YEAR>.csv
    
    Parameters:
        config (dict): The configuration dictionary (must include "state" and "year").
        
    Returns:
        str: The file path to the IPUMS data file, or None if the download fails.
    """
    base_data_dir = config["data_dir"]
    
    # Create the desired downloads folder: data/api_downloads/<STATE>/ipums_api_downloads
    desired_downloads_folder = os.path.join(base_data_dir, "api_downloads", config["state"], "ipums_api_downloads")
    if not os.path.exists(desired_downloads_folder):
        os.makedirs(desired_downloads_folder, exist_ok=True)
        logging.info(f"Created desired API downloads folder: {desired_downloads_folder}")
    
    # Construct the desired file name (e.g., FL_ipums_2022.csv) and full path.
    desired_file_name = f"{config['state']}_ipums_{config['year']}.csv"
    desired_file_path = os.path.join(desired_downloads_folder, desired_file_name)
    
    # If the file already exists, return its path.
    if os.path.exists(desired_file_path):
        logging.info(f"Found existing IPUMS data file: {desired_file_path}")
        return desired_file_path
    else:
        logging.info(f"No existing IPUMS file for {config['state']} {config['year']}. Fetching via API...")
        
        # Temporarily override the download_dir in api_settings to our desired folder.
        original_download_dir = config["api_settings"].get("download_dir", "api_downloads")
        config["api_settings"]["download_dir"] = desired_downloads_folder
        
        # Fetch the data via the API.
        df = fetch_ipums_data_api(config)
        if df is not None:
            try:
                # Save the DataFrame to our desired file path.
                df.to_csv(desired_file_path, index=False)
                logging.info(f"Downloaded IPUMS data saved to {desired_file_path}")
                # Optionally, restore the original download_dir.
                config["api_settings"]["download_dir"] = original_download_dir
                return desired_file_path
            except Exception as e:
                logging.error(f"Error saving IPUMS data to file: {e}")
                # Restore original download_dir even if saving fails.
                config["api_settings"]["download_dir"] = original_download_dir
                return None
        else:
            logging.error("Failed to fetch IPUMS data via API.")
            config["api_settings"]["download_dir"] = original_download_dir
            return None
def process_all_states(config):
    """
    Process HCV eligibility data for all states and years defined in the configuration.

    This function loops over each state in config["states"] and each year in config["ipums_years"],
    performing the following steps for each state-year combination:
      1. Update the configuration with state-specific file paths using template strings.
      2. Set the current state and year in the configuration.
      3. Create the state-year specific output directory.
      4. Update the HUD HCV data path with the current year.
      5. Check for (or download) the IPUMS data file and update config["ipums_data_path"] accordingly.
      6. Process the HCV eligibility data by calling process_hcv_eligibility with the updated configuration.
      7. After processing, delete the downloaded IPUMS file to prevent accumulation in the download folder.

    Parameters:
        config (dict): The global configuration dictionary containing:
            - "states": A list of state abbreviations.
            - "ipums_years": A list of years to process.
            - "data_dir": The base directory for data files.
            - "output_directory": The base output directory.
            - "hud_hcv_template": Template for the HUD HCV file path (which includes a {year} placeholder).
            - "api_settings": A dictionary of API settings (including "ipums_api_token" and "download_dir").
            - Other keys required by downstream processing functions.

    Returns:
        None
    """
    for state in config["states"]:
        for year in config["ipums_years"]:
            logging.info(f"Processing state: {state.upper()} for year: {year}")
            state_config = update_config_for_state(config, state)
            state_config["state"] = state.upper()
            state_config["year"] = year
            state_year_output = create_output_structure(config["output_directory"], state, year)
            state_config["output_directory"] = state_year_output
            state_config["hud_hcv_data_path"] = config["hud_hcv_template"].format(
                data_dir=config["data_dir"], state=state, year=year)
            ipums_file = get_ipums_data_file(state_config)
            if ipums_file is None:
                logging.error(f"Skipping {state.upper()} {year} due to IPUMS data download failure.")
                continue
            state_config["ipums_data_path"] = ipums_file
            process_hcv_eligibility(state_config)
            try:
                if os.path.exists(state_config["ipums_data_path"]):
                    os.remove(state_config["ipums_data_path"])
                    logging.info(f"Deleted downloaded IPUMS file: {state_config['ipums_data_path']}")
            except Exception as e:
                logging.error(f"Error deleting downloaded IPUMS file: {e}")
