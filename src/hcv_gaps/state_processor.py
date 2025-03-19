"""
State Processor Module for HCV Eligibility Analysis.

This module provides functions to process multiple states using a global configuration.
It includes:
  - update_config_for_state(config, state): Returns a state-specific config by substituting
    the state abbreviation into template strings.
  - process_all_states(config): Loops over the states in config["states"] and processes each state
    by calling the HCV processing function.
"""

import copy
import logging
from .hcv_processing import process_hcv_eligibility

def update_config_for_state(config, state):
    """
    Update the configuration dictionary for a specific state.

    This function takes the global config and a state abbreviation,
    and returns a new configuration dictionary with state-specific file paths
    updated using the template strings defined in the global config.

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
    state_config["hud_hcv_data_path"] = config["hud_hcv_template"].format(
        data_dir=config["data_dir"], state=state)
    return state_config

def process_all_states(config):
    """
    Process HCV eligibility data for all states defined in the configuration.

    This function loops over each state abbreviation in config["states"], generates
    a state-specific configuration using update_config_for_state, and then calls the core
    processing function process_hcv_eligibility with that updated configuration.

    Parameters:
        config (dict): The global configuration dictionary.
    """
    for state in config["states"]:
        logging.info(f"Processing state: {state}")
        state_config = update_config_for_state(config, state)
        process_hcv_eligibility(state_config)
