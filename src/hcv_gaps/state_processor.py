"""
State Processor Module.

Processes states and years specified in the global configuration by:
    - Updating paths in the configuration for each state and year.
    - Managing IPUMS data acquisition (local or via API).
    - Setting up appropriate output directory structures.
    - Delegating core data processing to the `process_hcv_eligibility` function.
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

    Parameters:
        config (dict): Global configuration dictionary.
        state (str): State abbreviation.

    Returns:
        dict: Updated configuration dictionary with state-specific file paths.
    """
    state_config = copy.deepcopy(config)
    state_config["crosswalk_2012_path"] = config["crosswalk_2012_template"].format(
        data_dir=config["data_dir"], state=state)
    state_config["crosswalk_2022_path"] = config["crosswalk_2022_template"].format(
        data_dir=config["data_dir"], state=state)
    state_config["incarceration_data_path"] = config["incarceration_template"].format(
        data_dir=config["data_dir"], state=state)
    # HUD HCV data path is year-specific and updated separately.
    return state_config


def get_ipums_data_file(config):
    """
    Get IPUMS data file path, fetch via IPUMS API if needed.

    Parameters:
        config (dict): Configuration including IPUMS API settings and user token.

    Returns:
        str: Path to the IPUMS data file.

    Raises:
        FileNotFoundError: Local file specified but missing.
        RuntimeError: API fetch fails or configuration logic error occurs.
    """
    local_path = config.get("ipums_data_path", "").strip()
    use_api = config.get("api_settings", {}).get("use_ipums_api", False)

    if not use_api and local_path and local_path.upper() != "API":
        if os.path.exists(local_path):
            logging.info(f"Using local IPUMS data: {local_path}")
            return local_path
        raise FileNotFoundError(f"Local IPUMS file not found: {local_path}")

    dl_dir = os.path.join(config["data_dir"], config["state"].lower(), "api_downloads", "ipums_api_downloads")
    os.makedirs(dl_dir, exist_ok=True)
    file_path = os.path.join(dl_dir, f"{config['state'].lower()}_ipums_{config['year']}.csv")

    logging.info("Fetching IPUMS data via API...")
    config["api_settings"]["download_dir"] = dl_dir
    df = fetch_ipums_data_api(config)
    if df is None:
        raise RuntimeError("IPUMS API fetch failed.")

    df.to_csv(file_path, index=False)
    logging.info(f"IPUMS data saved: {file_path}")
    return file_path


def process_all_states(config):
    """
    Process HCV eligibility data for all states and years specified in the configuration.

    Parameters:
        config (dict): Global configuration with states, years, paths, and API details.

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
            
            state_config["income_limits_path"] = config["income_limits_template"].format(
                data_dir=config["data_dir"], state=state, year=year)

            state_config["hud_hcv_data_path"] = config["hud_hcv_template"].format(
                data_dir=config["data_dir"], state=state, year=year)

            ipums_file = get_ipums_data_file(state_config)
            state_config["ipums_data_path"] = ipums_file

            if ipums_file:
                process_hcv_eligibility(state_config)
                try:
                    if os.path.exists(ipums_file):
                        os.remove(ipums_file)
                        logging.info(f"Deleted downloaded IPUMS file: {ipums_file}")
                except Exception as e:
                    logging.error(f"Error deleting downloaded IPUMS file: {e}")
