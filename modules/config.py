"""
Configuration file for HCV analysis scripts.

This file contains paths to the CSV files and other configuration options 
used in the HCV analysis process.

Attributes:
    CONFIG (dict): A dictionary containing configuration options, including file paths
                   and various processing options.

    - ipums_data_path: str, Path to the IPUMS dataset CSV file.
    - crosswalk_data_path: str, Path to the MCDC crosswalk dataset CSV file.
    - income_limits_path: str, Path to the income limits dataset CSV file.
    - incarceration_data_path: str, Path to the incarceration dataset CSV file.
    - hud_hcv_data_path: str, Path to the HUD Picture of Subsidized Housing CSV file.
    - output_directory: str, Path to the directory where output files should be saved.
    - verbose: bool, If True, print readouts/updates during processing.
    - prisoners_identified_by_GQTYPE2: bool, If True, use GQTYPE == 2 to identify prisoners directly.
    - race_sampling: bool, If True, perform race-based sampling when adjusting eligibility for incarcerated individuals.
    - display_race_stats: bool, If True, include race statistics in the summary table output.

Usage:
    To use this configuration, simply import this file in your script and access the CONFIG dictionary.
    Make sure to update the file paths and file names to match the location of your CSV files.

Example:
    CONFIG = {
        "ipums_data_path": "/Users/your_username/Desktop/HCV CSV FILES/path_to_ipums_data.csv",
        "crosswalk_data_path": "/Users/your_username/Desktop/HCV CSV FILES/path_to_crosswalk_data.csv",
        "income_limits_path": "/Users/your_username/Desktop/HCV CSV FILES/path_to_income_limits.csv",
        "incarceration_data_path": "/Users/your_username/Desktop/HCV CSV FILES/path_to_incarceration_data.csv",
        "hud_hcv_data_path": "/Users/your_username/Desktop/HCV CSV FILES/path_to_hud_hcv_data.csv",
        "output_directory": "/Users/your_username/Desktop/HCV Outputs/",
        "verbose": True,
        "prisoners_identified_by_GQTYPE2": False,
        "race_sampling": True,
        "display_race_stats": False
    }
"""

CONFIG = {
    "ipums_data_path": "path_to_ipums_data.csv",
    "crosswalk_data_path": "path_to_crosswalk_data.csv",
    "income_limits_path": "path_to_income_limits.csv",
    "incarceration_data_path": "path_to_incarceration_data.csv",
    "hud_hcv_data_path": "path_to_hud_hcv_data.csv",
    "output_directory": "path_to_output_directory",
    "verbose": False,
    "prisoners_identified_by_GQTYPE2": False,
    "race_sampling": False,
    "display_race_stats": False
}
