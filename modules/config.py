"""
Configuration file for HCV analysis scripts.

This file contains paths to the CSV files and other configuration options 
used in the HCV analysis process.

Attributes:
    CONFIG (dict): A dictionary containing configuration options, including file paths
                   and various processing options.

    - ipums_data_path: str, Path to the IPUMS dataset CSV file.
    - crosswalk_2012_path: str, Path to the 2012 MCDC crosswalk dataset CSV file.
    - crosswalk_2022_path: str, Path to the 2022 MCDC crosswalk dataset CSV file.
    - income_limits_path: str, Path to the income limits dataset CSV file.
    - incarceration_data_path: str, Path to the incarceration dataset CSV file.
    - hud_hcv_data_path: str, Path to the HUD Picture of Subsidized Housing CSV file.
    - output_directory: str, Path to the directory where output files should be saved.
    - verbose: bool, If True, enables logging at INFO level for workflow updates.
    - prisoners_identified_by_GQTYPE2: bool, If True, use GQTYPE == 2 to identify prisoners directly.
    - race_sampling: bool, If True, perform race-based sampling when adjusting eligibility for incarcerated individuals.
    - display_race_stats: bool, If True, include race statistics in the summary table output.

Usage:
    To use this configuration, import this file in your script and access the CONFIG dictionary.
    Update the file paths according to your system.

Example:
    CONFIG = {
        "ipums_data_path": "path_to_ipums_data.csv",
        "crosswalk_2012_path": "path_to_geocorr_puma2012.csv",
        "crosswalk_2022_path": "path_to_geocorr_puma2022.csv",
        ...
    }
"""

# Define the configuration dictionary
CONFIG = {
    "ipums_data_path": "path_to_ipums_data.csv",
    "crosswalk_2012_path": "path_to_geocorr_puma2012.csv",
    "crosswalk_2022_path": "path_to_geocorr_puma2022.csv",
    "income_limits_path": "path_to_hud_income_limits.csv",
    "incarceration_data_path": "path_to_incarceration_data.csv",
    "hud_hcv_data_path": "path_to_hud_hcv_picsubhhds.csv",
    "output_directory": "path_to_output_directory",
    "verbose": False,
    "prisoners_identified_by_GQTYPE2": False,
    "race_sampling": True,
    "display_race_stats": True,
}
