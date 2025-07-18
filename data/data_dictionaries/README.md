# Data Dictionaries

This directory contains the machine-readable data dictionaries for the two primary HUDLink outputs:

1. **Eligibility Data** (`eligibility_datadict_final.csv`)  
   Describes all fields in the per-household “eligibility” DataFrame, including:
   - **IPUMS variables** imported directly from the ACS microdata (see the IPUMS codebook for full definitions)  
   - **Script-generated fields** for family splitting, weight reallocation, and PUMA-to-county crosswalking  
   - **Demographic indicator flags** (prefixed `elig_`) that mark households by household type, age, race/ethnicity, tenure, disability status, etc.  
   - **Income-limit thresholds** (30%, 50%, 80% AMI) and corresponding weighted eligibility counts  

2. **Summary Data** (`summary_df_datadict.csv`)  
   Describes all fields in the county-level summary DataFrame, including:
   - **Aggregate eligibility metrics** (total and demographic-specific weighted counts and percentages at each AMI threshold)  
   - **HUD Picture of Subsidized Households (PSH)** linkage variables (e.g. program_label, total_units, rent_per_month, etc. – see the HUD PSH data dictionary for details)  
   - **Geographic and temporal metadata** (county names, quarters, summary levels, etc.)

---

### Notes on Naming Conventions

- To keep the dictionaries concise, related fields have been **grouped** in the descriptions.  
  For example, rather than listing each HUD AMI limit variable (`il30_p1`, `il30_p2`, …), we describe them collectively as “AMI 30% income limits for households of 1–8 persons.”  
- Similarly, demographic eligibility flags follow a consistent `elig_<criterion>` pattern; their CSV labels map directly to the corresponding `elig_*` columns in the code.

---
