"""
File Utilities Module.

This module provides functions for creating output directories.
Specifically, it creates a root output directory (e.g., on the user's Desktop),
and for each state and year combination, it creates:
  - A state folder
  - Within that state folder, a subfolder named with the state and year (e.g., FL_2019)
"""

import os
import logging

def create_output_structure(root_output, state, year):
    """
    Creates the complete output directory structure for a given state and year.

    The structure will be:
      root_output/                (e.g., C:/Users/<user>/Desktop/HCV_GAPS_output)
          STATE/                 (e.g., FL)
              STATE_YEAR/        (e.g., FL_2019)

    Parameters:
        root_output (str): The base output directory path.
        state (str): The state abbreviation.
        year (int or str): The year.

    Returns:
        str: The full path to the final directory created for the state and year.
    """
    # Check if root output directory already exists.
    if not os.path.exists(root_output):
        os.makedirs(root_output)
        logging.info("Created root output directory: " + root_output)

    # Create the state folder (using uppercase for consistency)
    state_dir = os.path.join(root_output, state.upper())
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)
        logging.info("Created state directory: " + state_dir)

    # Create the state_year folder (e.g., FL_2019)
    final_dir = os.path.join(state_dir, "{}_{}".format(state.upper(), year))
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)
        logging.info("Created output directory for {} {}: {}".format(state.upper(), year, final_dir))

    return final_dir

def get_default_output_directory():
    """
    Determines the user's Desktop and returns a default output directory path.

    Returns:
        str: The default output directory path on the user's Desktop.
    """
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    default_output = os.path.join(desktop, "HCV_GAPS_output")
    return default_output
