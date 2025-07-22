# -*- coding: utf-8 -*-
"""
Test Configuration Module for hudlink.

This module defines the test configuration dictionary used for testing the hudlink 
pipeline. The configuration points to test datasets
and sets appropriate parameters for automated testing.

Test Data Structure:
    The test configuration expects data files organized as:
    
    tests/test_data/
    ├── ipums_test_data.csv                    # Sampled IPUMS microdata  
    └── test/                                  # Test state folder
        ├── test_geocorr_puma_2012.csv         # 2012 crosswalk data
        ├── test_geocorr_puma_2022.csv         # 2022 crosswalk data  
        ├── test_income_limits/
        │   └── test_test_income_limits.csv    # HUD income limits
        └── test_hud_pic_sub_housing/
            └── test_hud_hcv_picsubhhds_test.csv  # HUD subsidized housing data

Usage:
    from tests.test_config import CONFIG
    from hudlink.hudlink_processing import process_eligibility
    
    # Run pipeline with test data
    process_eligibility(CONFIG)

Note:
    - Ipums test data is a sampled version of real ipums 5-year ACS data
    - All other test datasets are full versions of real data, 
    - API functionality is disabled (use_ipums_api: False)
    - Outputs are written to tests/temp_outputs/ for easy cleanup
"""

CONFIG = {
    # === DATA SOURCE CONTROLS ===
    "ipums_data_path": "tests/test_data/ipums_test_data.csv",  # path to ipums test data
    "output_directory": "tests/temp_outputs",

    # === MAIN USER INPUTS ===
    "state": "test",
    "year": "test",    
    "program_labels": [       
        "Summary of All HUD Programs" 
    ],

    # === INPUT TEST DATA LOCATION ===
    "data_dir": "tests/test_data",  # Base directory for all state-specific input files

    "crosswalk_2012_path": "tests/test_data/test_geocorr_puma_2012.csv",
    "crosswalk_2022_path": "tests/test_data/test_geocorr_puma_2022.csv",
    "income_limits_path":   "tests/test_data/test_income_limits/test_test_income_limits.csv",
    "hud_psh_data_path":         "tests/test_data/test_hud_pic_sub_housing/test_hud_hcv_picsubhhds_test.csv",

    # === PROCESSING OPTIONS ===
    "verbose": False,
    "exclude_group_quarters": False,  
    "race_sampling": False,                    
    "split_households_into_families": False,   
    "income_limit_agg": "max",   
    
    # === API SETTINGS ===
    "api_settings": {
        "use_ipums_api": False,
        "download_dir": "data/api_downloads",   
        "clear_api_cache": True
    },
}
