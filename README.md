# County Level Housing Choice Voucher Gap Calculation

## Overview
This repository contains modules that can be used to calculate voucher gaps at the county level. The code was designed specifically to handle ACS data for Florida, but it can be adjusted easily as needed for other states.

## Objectives
- Demonstrate the functionality of the HCV Gap Calculation methodology.
- Provide a step-by-step guide to loading, processing, and analyzing the data.
- Visualize the results and provide a summary of the findings.

## Workflow
The project follows these key steps:
1. **Imputation of Missing County Data**: Import necessary datasets including IPUMS data, crosswalk data from Geocorr 2018, and use these to fill in missing county values in the ACS dataset.
2. **Family Size and Income Variables Cleaning**: Clean income data, accounting for distinct family incomes in multifamily households, and check for anomalies.
3. **Multifamily Household Split and Income Cleaning**: Split multifamily households into distinct family-level households, assigning new unique serial numbers and performing a final income check.
4. **Household Weight Adjustment**: Adjust the HHWT variable to ensure accurate representation of household weights after splitting multifamily households.
5. **Optional Aggregation and Flattening**: Aggregate various family characteristics and condense the data into one row per family.
6. **Eligibility Determination**: Calculate HCV eligibility based on family income and size, comparing with HUD's published income limits.
7. **Removing Incarcerated Individuals via Stratified Selection**: Adjust eligibility counts to remove incarcerated individuals using data from the Florida Department of Corrections and the Federal Bureau of Prisons.
8. **Generate Final Outputs**: Calculate the voucher gap and save the results, comparing eligibility counts with voucher allocation data from HUD.

## Installation
To get started, clone the repository and install the required dependencies:

```bash
git clone https://github.com/sdabney5/HCVGAPS.git
cd HCVGAPS
pip install -r requirements.txt
```

## Configuration
Update the `config.py` file with paths to your data files:
```python
CONFIG = {
    'ipums_data_path': 'path/to/ipums_data.csv',
    'crosswalk_data_path': 'path/to/crosswalk_data.csv',
    'income_limits_path': 'path/to/income_limits.csv',
    'incarceration_data_path': 'path/to/incarceration_data.csv',
    'hud_hcv_data_path': 'path/to/hud_hcv_data.csv',
    'output_directory': 'path/to/output_directory',
    'prisoners_identified_by_GQTYPE2': True,
    'race_sampling': True,
    'verbose': True,
    'display_race_stats': True,
}
```

## Usage
To run the main script and process the data, follow these steps:

1. **Open a Command Prompt or Terminal:**
   - On Windows: Search for "Command Prompt" and open it.
   - On mac: Open "Terminal" from Applications > Utilities folder.

2. **Navigate to the Project Directory:**
   - Use the `cd` command to change the directory to where you cloned the repository. For example:
   ```bash
   cd path/to/HCVGAPS
   ```
3. **Run the Main Script:**
   - Once you are in the project directory, type the following command and press Enter
   ```bash
   python main.py
   ``` 
   - This will execute the main script and process the data according to the configuration specified in config.py.

## License
This project is licensed under the MIT License

## Contact
For any questions or issues, please contact sdabney@fsu.edu

## Contributing
Contributions are welcome! Please read the CONTRIBUTING.md file for guidelines.


