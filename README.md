# HCVGAPS: County-Level Housing Choice Voucher Gap Calculation

## Overview
HCVGAPS is a Python-based framework for calculating county-level Housing Choice Voucher gaps across the United States. The methodology expands upon previous research (Dabney, 2024) by scaling the analysis from **Florida** to a **nationwide scope**, and incorporating multi-year crosswalk datasets to improve county-level accuracy. Since **5-Year ACS datasets** span multiple years, and Geocorr updates crosswalks periodically, **multiple crosswalk datasets may be necessary for accurate county mapping**. For example, the **2022 5-Year ACS dataset** includes survey years from 2018 to 2022, meaning that survey data from 2022 should reference a **2022 Geocorr crosswalk**, while the other years in the dataset should reference the **2018 Geocorr crosswalk**. This method two-crosswalk-datasets method will be necessary until **2027**, when a single crosswalk dataset (e.g., Geocorr 2022) will be sufficient.

## Key Features
- **Handles national- or state-level HCV analysis** (previously Florida-only).
- **Allows multiple Geocorr crosswalk datasets** (2018 and 2022).
- **Accounts for multifamily households** by splitting and weighting families within shared housing units.
- **Incorporates incarceration data** to adjust HCV eligibility estimates.
- **Computes voucher gaps and allocation rates** at county and state levels, with optional race-based analysis.
- **Fully automated workflow**—data loading, processing, and final report generation.

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
git clone https://github.com/sdabney5/HCVGAPS.git
cd HCVGAPS
pip install -r requirements.txt
```

## Configuration
Update the `config.py` file to specify your dataset paths:
```python
CONFIG = {
    "ipums_data_path": "sample_data/sample_fl_ipums.csv",
    "crosswalk_2012_path": "sample_data/sample_fl_geocorr_puma2012.csv",
    "crosswalk_2022_path": "sample_data/sample_fl_geocorr_puma2022.csv",
    "income_limits_path": "sample_data/sample_fl_income_limits.csv",
    "incarceration_data_path": "sample_data/sample_fl_incarceration.csv",
    "hud_hcv_data_path": "sample_data/sample_fl_hud_hcv.csv",
    "output_directory": "output/",
    "prisoners_identified_by_GQTYPE2": True,
    "race_sampling": True,
    "verbose": True,
    "display_race_stats": True,
}
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

## Sample Data
This repository includes **sample datasets** in `sample_data/` for testing:
- `sample_fl_ipums.csv` – Sample IPUMS dataset for Florida.
- `sample_fl_geocorr_puma2012.csv` – Geocorr 2012 crosswalk sample.
- `sample_fl_geocorr_puma2022.csv` – Geocorr 2022 crosswalk sample.
- `sample_fl_income_limits.csv` – HUD income limits sample.
- `sample_fl_hud_hcv.csv` – HUD Picture of Subsidized Households sample.
- `sample_fl_incarceration.csv` – Sample incarceration dataset.

## Acknowledgments
Special thanks to **Iris Bui** and **Mira Scannapieco**, UROP interns at Florida State University, for their assistance with data processing and methodology refinement.

## Funding
This project was supported by a grant from the **Institute for Humane Studies**.

## License
This project is licensed under the MIT License.

## Contact
For questions or issues, contact **sdabney@fsu.edu**

## Citation
If you use this methodology, please cite:
Dabney, Shane. 2024. *Calculating County-Level Housing Choice Voucher Gaps: A Methodology.* Cityscape (Washington, D.C.) 26 (2): 401–12.

## Contributing
Contributions are welcome! See `CONTRIBUTING.md` for guidelines.
