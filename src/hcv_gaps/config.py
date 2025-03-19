"""
Configuration file for HCV analysis scripts.

This file contains paths to the CSV files and other configuration options
used in the HCV analysis process. It also supports processing multiple states by including:
- A list of state abbreviations (users can modify as needed).
- A base directory for state-specific data (relative to the repository root).
- Template strings for state-specific file paths.

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
      - states: list, A list of state abbreviations to process.
      - data_dir: str, Base directory for state-specific data.
      - [Template strings]: Templates for state-specific file paths that will be used to update
        the core keys (e.g., "crosswalk_2012_path") dynamically.

Usage:
    To use this configuration, import this file in your script and access the CONFIG dictionary.
    Update the file paths according to your system.

Example:
    For state "ak" (Alaska), the expected files are:
      - ak_geocorr_puma_2012.csv
      - ak_geocorr_puma_2022.csv
      - ak_hud_income_limits_2022.csv
      - ak_incarc_data.csv
      - ak_hud_hcv_picsubhhds_2022.csv

The core keys (e.g., "crosswalk_2012_path") used by the processing modules
will be updated dynamically using the template strings.
"""

CONFIG = {
    # User defined file paths:
    "ipums_data_path": "path_to_ipums_data.csv",
    "output_directory": "path_to_output_directory",

    # List of state abbreviations to process (users can add or remove as needed):
    "states": ["al", "ak", "az", "ar", "ca", "co", "ct", "de", "fl", "ga", "hi", "id",
               "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms",
               "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok",
               "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "vt", "va", "wa", "wv",
               "wi", "wy", "dc"],

    # Base directory for state-specific data (relative to the repository root)
    "data_dir": "data",

    # Template strings for state-specific file paths.
    # The {data_dir} placeholder will be replaced with the value from "data_dir"
    # and the {state} placeholder will be replaced with the state abbreviation.
    "crosswalk_2012_template": "{data_dir}/{state}/{state}_geocorr_puma_2012.csv",
    "crosswalk_2022_template": "{data_dir}/{state}/{state}_geocorr_puma_2022.csv",
    "income_limits_template": "{data_dir}/{state}/{state}_hud_income_limits_2022.csv",
    "incarceration_template": "{data_dir}/{state}/{state}_incarc_data.csv",
    "hud_hcv_template": "{data_dir}/{state}/{state}_hud_hcv_picsubhhds_2022.csv",

    # Other configuration options:
    "verbose": False,
    "prisoners_identified_by_GQTYPE2": False,
    "race_sampling": True,
    "display_race_stats": True,
}
