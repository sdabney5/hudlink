# Data Directory

This directory contains all raw and processed data used by the hudlink script, organized by state, plus a `data_dictionaries/` folder with definitions.

### `data_dictionaries/`

Contains the machine-readable data dictionaries for hudlink outputs:

- **Eligibility Data** (`eligibility_datadict_final.csv`)  
- **Summary Data** (`summary_df_datadict.csv`)

### State Folders (`<state_abbr>/`)

Each state folder contains three subdirectories:

1. **`<state>_hud_fmr/`**  
   – Fair Market Rent (FMR) data for 2022 directly from HUD.  
   – Source: HUD FMR tables  
   – URL: https://www.huduser.gov/portal/datasets/fmr.html

2. **`<state>_hud_pic_sub_housing/`**  
   – Picture of Subsidized Housing (PSH) data for 2006–2023 directly from HUD’s Picture of Subsidized Housing dataset.  
   – Source: HUD PSH data  
   – URL: https://www.huduser.gov/portal/datasets/picture_of_subsidized_housing.html

3. **`<state>_income_limits/`**  
   – Section 8 income limits for 2006–2023 directly from HUD’s income limits tables.  
   – Source: HUD Income Limits  
   – URL: https://www.huduser.gov/portal/datasets/il.html
