# hudlink: Multi-Program Housing Subsidy Coverage Analysis

## Overview
hudlink provides two core outputs:

1. Household-level eligibility DataFrame: flags every ACS household as eligible or not at 30%, 50%, and 80% HUD AMI income-limit thresholds, with full access to any IPUMS ACS variables.

2. County-level summaries: produces separate summary DataFrames for each HUD program plus an “All HUD programs” view, optionally including counts and percentages by sensitive variables (default set provided, user‑extensible).

Works for any ACS year from 2007 through 2023.

This project builds upon the original HCVGAPS methodology (Dabney 2024), extending scope from voucher-only to a multi-program analysis. See Citation below for details.


## Key Features
- **Micro and Macro outputs:** Produces a full eligibility DataFrame of ACS households plus a linked county‑level summary for PSH data.
- **Configurable analysis:** Select states, years, HUD Programs, ACS variables, and (optionally) split multi family households into separate households by family, via a single CONFIG dictionary
- **API integration:** Optional IPUMS API fetch of ACS PUMS data (requires a valid token in secrets/ipums_token.txt)
- **Fully automated, reproducible workflow:** results can be replicated on any machine

## Important Considerations for County Equivalents
Some states have **county equivalents** that require manual adjustments for accurate county-level mapping. These include:
- **Virginia** (Independent cities are county equivalents)
- **Louisiana** (Uses **parishes** instead of counties)
- **Alaska** (Has boroughs and census areas instead of counties)
- **Connecticut** (Recently changed its county equivalents)

Additionally, **cities that serve as county-equivalents** need to be accounted for in the dataset. This will mean making sure the county-equivalent names are consistent across all datasets--(e.g. You may need  to change "Parish" or "Census Area" to "County", and "city" to "city County" for the script to recognize the county-equivalent,)

## Methodology
This version follows an expanded methodology:
1. **Data Sources:** Loads data from IPUMS USA, HUD’s Picture of Subsidized Households, HUD’s Income Limits, Geocorr crosswalks, and Vera Institute incarceration data.
2. **County Imputation:** Uses **dual crosswalk datasets** (2018 & 2022) to infer county data when missing, with **population-based allocation factors** for PUMA-to-county mapping.
3. **Family-Level Processing:** Cleans income data, splits multifamily households, and **adjusts statistical weights (`HHWT`)** to maintain representativeness.
4. **HCV Eligibility Calculation:** Determines HCV eligibility by comparing family size and income to HUD’s county-specific income limits (30%, 50%, 80% thresholds).
5. **Incarceration Adjustment:** Removes incarcerated individuals from eligibility estimates based on county-level prison data.
6. **Final Voucher Gap Computation:** Compares eligible households to available HCVs, calculating **allocation rates** and optional **race-specific disparities.**
7. **Outputs & Reporting:** Saves final county-level CSV reports, with optional Tableau visualization integration.

## Installation
Clone the repository and install required dependencies:
```
git clone https://github.com/sdabney5/hudlink.git
cd hudlink
pip install -r requirements.txt
```

## Configuration
Update the `config.py` file to specify your dataset paths:
```python
# Configuration settings for the hudlink pipeline
# File: src/hudlink/config.py
import os
from .file_utils import get_default_output_directory, load_ipums_api_token

# Load IPUMS API token from secrets/ipums_token.txt
ipums_token_path = os.path.join("secrets", "ipums_token.txt")
ipums_api_token = load_ipums_api_token(ipums_token_path)

CONFIG = {
    # Data source controls
    "ipums_data_path": "API",          # "API" triggers IPUMS fetch; or set a local CSV path
    "output_directory": get_default_output_directory(),

    # Main user inputs
    "states": ["fl"],           # e.g. ["fl","ak","ct"]
    "ipums_years": [2023],      # e.g. [2021, 2022]
    "program_labels": [                   #include any 'program_labels' values from HUD's PSH dataset
        "Summary of All HUD Programs",
        "Public Housing",
        "Housing Choice Vouchers",
    ],

    # Input data location
    "data_dir": "data",                # Base folder for state subdirectories
    "crosswalk_2012_template": "{data_dir}/{state}/{state}_geocorr_puma_2012.csv",
    "crosswalk_2022_template": "{data_dir}/{state}/{state}_geocorr_puma_2022.csv",
    "income_limits_template":   "{data_dir}/{state}/{state}_income_limits/{state}_{year}_income_limits.csv",
    "incarceration_template":   "{data_dir}/{state}/{state}_incarc_data.csv",
    "hud_psh_template":         "{data_dir}/{state}/{state}_hud_pic_sub_housing/{state}_hud_hcv_picsubhhds_{year}.csv",

    # Processing toggles
    "verbose": False,
    "exclude_group_quarters": False,
    "race_sampling": True,
    "split_households_into_families": True,
    "income_limit_agg": "max",

    # API settings
    "api_settings": {
        "use_ipums_api": True,
        "ipums_api_token": ipums_api_token,
        "download_dir": "data/api_downloads",
        "clear_api_cache": True,
    },
}}
```

## Usage
### **Running the Full Workflow**
1. **Open a Command Prompt or Terminal:**
   ```
   cd path/to/HCVGAPS
   ```
2. **Execute the Main Script:**
   ```
   python main.py
   ```
3. **Results:** Final CSV outputs are saved in the `output/` directory.

## Acknowledgments
Special thanks to **Iris Bui** and **Mira Scannapieco**, UROP interns at Florida State University, for their assistance with data processing and methodology refinement.

## Funding
This project was supported by a grant from the **Institute for Humane Studies**.

## License
This project is licensed under the MIT License.

## Contact
For questions or issues, contact **sdabney@fsu.edu**

## Citation
This implementation is based on the HCVGAPS methodology:Dabney, Shane. “Calculating County-Level Housing Choice Voucher Gaps: A Methodology.” Cityscape 26, no. 2 (2024): 401–12.

If you use hudlink, please cite:Dabney, Shane. hudlink: Multi-Program Housing Subsidy Coverage Analysis. Version 2.0.0, 2025.

## Contributing
Contributions are welcome! See `CONTRIBUTING.md` for guidelines.
