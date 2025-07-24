
# hudlink

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![PyPI version](https://badge.fury.io/py/hudlink.svg)](https://badge.fury.io/py/hudlink)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

Automated ACS-HUD data linking for housing analysis: eligibility determination, protected-class analysis, and analysis-ready county summaries.

## Summary

hudlink provides reliable, high-quality, reproducible datasets for housing economists, researchers, planners, and policy makers. It automatically downloads, processes, and links American Community Survey (ACS) microdata with HUD's Picture of Subsidized Housing data to produce analysis-ready datasets at both household and county levels.

**Key Features:**
- Automated data integration from multiple federal sources (IPUMS ACS, HUD PSH, HUD Income Limits)
- Household-level HUD program eligibility determination at 30%, 50%, and 80% AMI thresholds
- Protected class demographic analysis for fair housing research
- County-level program allocation rates and gap analysis
- Reproducible research workflows with comprehensive configuration options

## Installation

### Option 1: Clone Repository (Recommended)

This is the main recommended approach - it allows full customization through the configuration file:

```
git clone https://github.com/sdabney5/hudlink.git
cd hudlink
pip install -e .
```

### Option 2: Install from PyPI

For users who want a simple installation without customization options:

```
pip install hudlink
```

## Prerequisites

### IPUMS API Token (Required)

hudlink uses the IPUMS USA API to download ACS microdata. You'll need a free IPUMS account:

1. **Register** at [https://usa.ipums.org/usa/](https://usa.ipums.org/usa/)
2. **Get your API token** from your account dashboard
3. **Add your token** to the existing secrets file:
   - Open the `secrets` folder in your hudlink directory
   - Open the file `ipums_token.txt`
   - Replace `YOUR TOKEN HERE` with your actual IPUMS API token
   - Save the file

## Quick Start

### Main Method: Configuration File (Recommended)

If you cloned the repository (recommended), customize your analysis by editing `src/hudlink/config.py`:

```python
CONFIG = {
    # Geographic and temporal scope
    "states": ["FL", "CA", "NY"],              # State abbreviations
    "ipums_years": [2022, 2023],               # ACS 5-year estimates
    
    # HUD program selection
    "program_labels": [
        "Summary of All HUD Programs",
        "Housing Choice Vouchers", 
        "Public Housing",
        "LIHTC"
    ],
    
    # Advanced processing options
    "split_households_into_families": True,    # Family vs household analysis
    "exclude_group_quarters": False,           # Remove institutional populations
    "income_limit_agg": "max",                 # Multiple income limit handling
    
    # Custom variable selection
    "additional_ipums_vars": "CLASSWKR,TRANWORK,GRADEATT",  # Employment, commute, education
    
    # Output settings
    "output_directory": "./outputs",
    "api_settings": {
        "use_ipums_api": True,                 # Automatic data download
        "clear_api_cache": True                # Clean up temporary files
    }
}
```

Then run:
```
cd hudlink
python -m hudlink.main
```

### Alternative: Command Line Interface

hudlink also provides a CLI for quick analyses without editing the config file:

```
# Basic usage - Florida and Texas, 2023 data
hudlink --states FL TX --years 2023

# Multiple years and custom output directory
hudlink --states CA NY --years 2022 2023 --output-dir ./my_analysis

# Include additional IPUMS variables
hudlink --states FL --years 2023 --additional-vars "CLASSWKR,TRANWORK,GRADEATT"

# Advanced options
hudlink --states FL --years 2023 \
        --split-families \
        --exclude-group-quarters \
        --income-agg median \
        --programs "Housing Choice Vouchers" "Public Housing"
```

**CLI Options:**
- `--states`: State abbreviations (e.g., FL CA NY)
- `--years`: ACS years to process (e.g., 2022 2023)
- `--output-dir`: Output directory path
- `--additional-vars`: Additional IPUMS ACS variables (comma-separated)
- `--split-families`: Split multi-family households for family-level analysis
- `--exclude-group-quarters`: Exclude group quarters from eligibility counts
- `--income-agg`: Income limit aggregation method (max, min, mean, median, mode)
- `--programs`: Specific HUD programs to analyze
- `--help`: Show detailed help with all options

### Python Scripts

For programmatic control and integration into larger analysis workflows:

For programmatic control and custom workflows:

```python
from hudlink import process_eligibility
from hudlink.config import CONFIG

# Basic usage with default settings
eligibility_df, summary_df = process_eligibility(
    states=["FL", "GA"], 
    years=[2023],
    ipums_api_token="your_token_here"
)

# Advanced configuration
custom_config = CONFIG.copy()
custom_config.update({
    "split_households_into_families": True,
    "additional_ipums_vars": "CLASSWKR,TRANWORK,GRADEATT",
    "exclude_group_quarters": True,
    "income_limit_agg": "median"
})

eligibility_df, summary_df = process_eligibility(
    states=["FL", "CA", "NY"],
    years=[2022, 2023],
    config=custom_config,
    ipums_api_token="your_token_here"
)
```

### Configuration File (For Cloned Repository)

If you cloned the repository, you can customize analysis by editing `src/hudlink/config.py`:

```python
CONFIG = {
    # Geographic and temporal scope
    "states": ["FL", "CA", "NY"],              # State abbreviations
    "ipums_years": [2022, 2023],               # ACS 5-year estimates
    
    # HUD program selection
    "program_labels": [
        "Summary of All HUD Programs",
        "Housing Choice Vouchers", 
        "Public Housing",
        "LIHTC"
    ],
    
    # Advanced processing options
    "split_households_into_families": True,    # Family vs household analysis
    "exclude_group_quarters": False,           # Remove institutional populations
    "income_limit_agg": "max",                 # Multiple income limit handling
    
    # Custom variable selection
    "additional_ipums_vars": "CLASSWKR,TRANWORK,GRADEATT",  # Employment, commute, education
    
    # Output settings
    "output_directory": "./outputs",
    "api_settings": {
        "use_ipums_api": True,                 # Automatic data download
        "clear_api_cache": True                # Clean up temporary files
    }
}
```

Then run:
```
cd hudlink
python -m hudlink.main
```

## Output Files

hudlink produces two primary datasets:

### 1. Eligibility DataFrame (`*_eligibility_*.csv`)
Household/family-level microdata with:
- **Complete ACS variables**: All demographic and economic characteristics
- **Eligibility flags**: `Eligible_at_30%`, `Eligible_at_50%`, `Eligible_at_80%`
- **Protected class indicators**: Race, ethnicity, disability status, veteran status, age
- **Geographic identifiers**: County, PUMA for spatial analysis
- **Survey weights**: For population-representative estimates

### 2. Summary DataFrame (`*_summary_*.csv`)
County-level aggregations with:
- **Eligibility counts**: Total and demographic-specific weighted counts and percentages
- **HUD program data**: Linked Picture of Subsidized Housing administrative data
- **Allocation rates**: Units available / eligible households
- **Gap estimates**: Unmet housing need by county and demographic group

## Core Features

### Comprehensive Data Integration
- **IPUMS ACS Microdata**: 50+ demographic and economic variables via API
- **HUD Picture of Subsidized Housing**: Administrative data on program utilization
- **HUD Income Limits**: County-specific AMI thresholds for eligibility determination
- **Geographic Crosswalks**: PUMA-to-county allocation factors for all US counties

### Advanced Processing Capabilities
- **Family vs. Household Analysis**: Option to analyze multi-family households at family unit level
- **Protected Class Analysis**: Comprehensive demographic flags for fair housing research
- **Custom Variable Selection**: Include any IPUMS ACS variable beyond defaults
- **Income Limit Aggregation**: Handle multiple income limits per county (max, min, mean, median, mode)
- **Group Quarters Handling**: Option to exclude institutional populations

## Advanced Configuration Options

### Family vs. Household Analysis (`split_households_into_families`)

In some cases, a multi-family household contains 2 or more families that would individually qualify for housing vouchers. hudlink provides the option to 'split' these households into distinct families and determine their eligibility for HUD programs separately, rather than treating the entire household as a single unit.

This setting is turned off by default but can be enabled in the configuration:
```python
"split_households_into_families": True
```

This option provides more precise eligibility determination by analyzing each family unit independently, which can significantly impact eligibility counts in areas with high rates of multi-generational or multi-family households.

### Group Quarters Exclusion (`exclude_group_quarters`)

hudlink can exclude households listed in the census as living in group quarters (institutional populations such as nursing homes, prisons, college dormitories, etc.) from eligibility counts.

```python
"exclude_group_quarters": True  # Default: False
```

When enabled, these households will still appear in the eligibility dataset but will not be marked as eligible regardless of their income. This provides a more realistic estimate of households that could actually utilize housing assistance programs.

### Income Limit Aggregation (`income_limit_agg`)

For some states (such as Connecticut or Vermont), HUD assigns multiple income limits for each county. Since hudlink is not equipped to accommodate multiple limits per county, it aggregates them using a specified method:

```python
"income_limit_agg": "max"  # Options: "max", "min", "mean", "median", "mode"
```

The default setting uses "max" to provide the most conservative (highest) eligibility threshold, resulting in more conservative eligibility count estimates. Using "min" would provide the most restrictive eligibility criteria.

### Custom Variable Selection (`additional_ipums_vars`)

Beyond the comprehensive default variables, you can include any IPUMS ACS variable in your analysis:

```python
"additional_ipums_vars": "CLASSWKR,TRANWORK,GRADEATT"  # Employment, commute, education variables
```

This allows for unlimited exploration of relationships between housing eligibility and other socioeconomic characteristics. See the [IPUMS variable list](https://usa.ipums.org/usa-action/variables/group) for all available options.

### Supported HUD Programs
- Housing Choice Vouchers (Section 8)
- Public Housing
- Low-Income Housing Tax Credit (LIHTC)
- Section 236/BMIR
- Section 8 New Construction/Substantial Rehabilitation
- 811/PRAC (Disabled)
- 202/PRAC (Elderly)
- Multi-Family Other programs

## Research Applications

### Policy Analysis
- Estimate unmet housing assistance need by county and demographic group
- Identify geographic and demographic disparities in program coverage
- Evaluate allocation efficiency across different HUD programs

### Academic Research
- Analyze correlations between housing assistance eligibility and economic outcomes
- Study geographic patterns of housing need and program accessibility
- Examine demographic disparities in federal housing program coverage

### Applied Research Examples

**Fair Housing Analysis:**
Researchers can filter the eligibility dataset for voucher-eligible households and analyze patterns by protected characteristics such as race, ethnicity, and disability status. For example: "Of all housing voucher-eligible households in Orange County, CA, what percentage are Black non-Hispanic veterans with a college education?" This type of analysis helps identify potential disparities in housing assistance access across demographic groups.


**Geographic Disparity Analysis:**

Using the summary dataset, researchers can calculate allocation rates (available units divided by eligible households) and identify counties with the highest unmet housing need. This analysis reveals geographic patterns of housing assistance coverage and can inform policy decisions about resource allocation and program expansion priorities.

**Program Efficiency Assessment:**
By comparing eligibility counts across different AMI thresholds (30%, 50%, 80%) with actual program utilization data from HUD's Picture of Subsidized Housing, researchers can evaluate how effectively different HUD programs are reaching their target populations and identify potential barriers to program access.

## System Requirements

- **Python**: 3.9 or higher
- **Memory**: 4GB+ RAM recommended for large states
- **Storage**: ~1-2 GB per state-year combination
- **Internet**: Required for automated data downloads
- **IPUMS Account**: Free registration at [https://usa.ipums.org/usa/](https://usa.ipums.org/usa/)

## Data Sources and Methodology

hudlink integrates data from multiple authoritative federal sources:

1. **IPUMS USA**: American Community Survey microdata with comprehensive demographic and economic variables
2. **HUD Picture of Subsidized Housing**: Administrative records on federal housing assistance programs
3. **HUD Income Limits**: County-specific Area Median Income (AMI) thresholds for program eligibility
4. **MCDC Crosswalks**: Geographic allocation factors for PUMA-to-county mapping

The methodology follows established practices for housing needs assessment and has been peer-reviewed (Dabney, 2024, *Cityscape*).

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Reporting bugs and requesting features
- Contributing code and documentation
- Development setup and testing procedures

## Citation

If you use hudlink in your research, please cite:

```bibtex
@software{dabney_hudlink_2025,
  author = {Dabney, Shane},
  title = {hudlink: Automated ACS-HUD Data Linking for Housing Analysis},
  version = {3.0.0},
  year = {2025},
  url = {https://github.com/sdabney5/hudlink},
  doi = {10.5281/zenodo.XXXXXXX}
}
```

**Related Publications:**
- Dabney, Shane. "Calculating County-Level Housing Choice Voucher Gaps: A Methodology." *Cityscape* 26, no. 2 (2024): 401–12.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://hudlink.readthedocs.io](https://hudlink.readthedocs.io) (coming soon)
- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/sdabney5/hudlink/issues)
- **Email**: [sdabney@fsu.edu](mailto:sdabney@fsu.edu) for methodological questions

## Acknowledgments

- **Research Assistants**: Iris Bui and Mira Scannapieco (UROP interns, Florida State University)
- **Funding**: Institute for Humane Studies
- **Data Providers**: IPUMS USA, U.S. Department of Housing and Urban Development
- **Institution**: Florida State University, Department of Urban & Regional Planning

---

*hudlink is developed and maintained by Shane Dabney at Florida State University.*