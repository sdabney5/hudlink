"""
Configuration settings for the hudlink analysis pipeline.

This module defines the CONFIG dictionary used across the project. It includes:
- File path templates for input data
- State/year lists for batch processing
- Which PSH program labels to link
- Toggles for incarceration data and verbosity
- API settings for optionally fetching IPUMS data automatically 
- API token loading

To use: import this module and access the CONFIG dictionary.
Ensure you run Python from the project root, so that "secrets/ipums_token.txt" resolves correctly.
"""

import os
from .file_utils import get_default_output_directory, load_ipums_api_token

# Path to the API token file (relative to project root)
ipums_token_path = os.path.join("secrets", "ipums_token.txt")

# Load the IPUMS token from the secrets file
ipums_api_token = load_ipums_api_token(ipums_token_path)

CONFIG = {
    # === DATA SOURCE CONTROLS ===
    "ipums_data_path": "API",  # Use "API" or "" to trigger IPUMS API fetch; or set a local CSV path
    "output_directory": get_default_output_directory(),

    # === MAIN USER INPUTS ===
    "states": ["hi", "dc"],         # Example: ["fl", "ak", "ct"]
    "ipums_years": [2023,2020],    # Example: [2021, 2022]
    "program_labels": [       # Which HUD PSH programs to produce linked summaries for
        "Summary of All HUD Programs", 
       # "Mod Rehab", 
        "Public Housing", 
       # "Section 236", 
      #  "Section 8 NC/SR",  
       # "LIHTC", 
        "Housing Choice Vouchers", 
      #  "Multi-Family Other",
      #  "811/PRAC",
       # "202/PRAC"
    ],

    # === INPUT DATA LOCATION ===
    "data_dir": "data",  # Base directory for all state-specific input files

    # Template strings for input file paths
    "crosswalk_2012_template": "{data_dir}/{state}/{state}_geocorr_puma_2012.csv",
    "crosswalk_2022_template": "{data_dir}/{state}/{state}_geocorr_puma_2022.csv",
    "income_limits_template":   "{data_dir}/{state}/{state}_income_limits/{state}_{year}_income_limits.csv",
    "incarceration_template":   "{data_dir}/{state}/{state}_incarc_data.csv",
    "hud_psh_template":         "{data_dir}/{state}/{state}_hud_pic_sub_housing/{state}_hud_hcv_picsubhhds_{year}.csv",

    # === PROCESSING OPTIONS ===
    "verbose": False,                          # Enables logging and reporting
    "exclude_group_quarters": False,  # if True, zeroes out eligibilities for any GQTYPE==2 rows
    "race_sampling": True,                    # Enables race-based prisoner eligibility adjustments
    "split_households_into_families": True,   # Use family-level weights vs. household-level
    "income_limit_agg": "max",   # one of ["min","max","median","mean"] for Counties with multiple Income Limits (e.g. in CT)
    
    # === API SETTINGS ===
    "api_settings": {
        "use_ipums_api": True,
        "ipums_api_token": ipums_api_token,
        "download_dir": "data/api_downloads",   # Where API-fetched files will be temporarily saved
        "clear_api_cache": True
    },
}
