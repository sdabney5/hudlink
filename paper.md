---
title: 'hudlink: A python package for linking ACS data to HUD PSH data for analysis and audits'
authors:
  - name: Shane Dabney
    affiliation: 1
    email: sdabney@fsu.edu

affiliations:
  - index: 1
    name: Florida State University

date: 17 March 2025

bibliography: references.bib

---

# Summary
hudlink is a Python-based framework for estimating county-level Housing Choice Voucher (HCV) gaps across the United States. It builds upon previous work (Dabney, 2024) by extending its geographic scope from Florida to all U.S. states and enhancing data integration for more accurate voucher allocation estimates. The framework automates the process of determining HCV eligibility, handling missing county data, and adjusting for incarcerated individuals, providing researchers and policymakers with a scalable tool for housing policy analysis.

# Statement of Need
Housing affordability remains a critical policy issue in the United States, and the Housing Choice Voucher program plays a key role in supporting low-income renters. However, understanding where voucher allocation gaps exist is challenging due to discrepancies in data availability, county-level aggregation issues, and multi-family household complexities. HCVGAPS addresses these challenges by:

- Using multiple crosswalk datasets to impute missing county values from Public Use Microdata Areas (PUMAs),
- Adjusting family and household weights for multi-family units,
- Integrating incarceration data to refine eligibility estimates,
- Computing voucher gaps by comparing eligibility counts to actual HCV allocations.

This framework provides a reproducible, scalable, and open-source solution for housing policy researchers studying voucher allocation disparities.

# Methodology
hudlink follows a structured workflow to estimate HCV gaps at the county level:
1. **Data Loading:** Imports ACS IPUMS data, HUD’s Picture of Subsidized Households, HUD income limits, incarceration data, and Geocorr crosswalks.
2. **County Imputation:** Uses **dual crosswalk datasets** (Geocorr 2018 & 2022) to impute missing county names for PUMA-based observations. If a PUMA spans multiple counties, the framework applies population-based allocation factors.
3. **Household Processing:** Splits multi-family households, cleans income variables, and adjusts statistical weights (`HHWT`) to ensure representativeness.
4. **Eligibility Calculation:** Determines voucher eligibility at the **30%, 50%, and 80% AMI thresholds**, based on HUD’s income limits.
5. **Prisoner Adjustment:** Excludes incarcerated individuals from eligibility estimates using county-level incarceration data.
6. **Voucher Gap Computation:** Compares eligibility counts to actual voucher allocations, computing HCV allocation rates and optional **race-based disparities.**
7. **Final Outputs:** Generates county-level CSV reports for use in statistical analysis and visualization.

# Key Features
- **National or State-Level Analysis:** Adapts to full national datasets or individual states.
- **Dual Crosswalk Integration:** Uses multiple Geocorr crosswalk datasets to improve county assignment.
- **Multi-Family Household Handling:** Ensures accurate representation of multi-family housing units.
- **Prisoner Exclusion Option:** Allows refining estimates by removing incarcerated individuals.
- **Automated Report Generation:** Produces structured output datasets for further analysis.

# Usage
hudlink is designed for **housing policy researchers**, **economists**, and **public sector analysts** who need a standardized methodology for estimating county-level voucher allocation gaps. The framework can be run with minimal setup by configuring dataset paths in `config.py` and executing:

```cmd
python main.py
```

# Acknowledgments
Special thanks to **Iris Bui** and **Mira Scannapieco**, UROP interns at Florida State University, for their contributions to data processing and methodology refinement.

This project was supported by a grant from the **Institute for Humane Studies**.

# References

