"""
API Calls Module for hudlink Analysis.

This module provides functions to fetch IPUMS USA data via the IPUMS API using ipumspy.
It supports 5-year ACS microdata extraction by:

- Mapping user configuration (state, year, variables) into a MicrodataExtract.
- Applying a state-level filter using FIPS codes.
- Submitting and monitoring the extract request.
- Downloading the DDI and microdata files.
- Loading the data into a pandas DataFrame.

Functions:
    - get_ipums_sample_code(year): Map year to IPUMS sample code.
    - get_state_fip(state_abbr): Map state abbreviation to FIPS code.
    - fetch_ipums_data_api(config): End-to-end extract, download, and load of IPUMS microdata.
"""

import logging
import gzip
import shutil
from datetime import datetime
from pathlib import Path
from ipumspy import IpumsApiClient, MicrodataExtract, readers  # Ensure ipumspy is installed

def get_ipums_sample_code(year):
    """
    Map a year to its corresponding 5-year ACS sample code.

    Parameters:
        year (int): The ACS 5-year extract year.

    Returns:
        str: IPUMS sample code (e.g., 'us2022c').

    Raises:
        ValueError: If the year is out of supported range (2009–current year).
    """
    current_year = datetime.now().year
    if year < 2009 or year > current_year:
        raise ValueError(f"Year must be between 2009 and {current_year}. Provided: {year}")

    mapping = {
        2009: "us2009e", 2010: "us2010e", 2011: "us2011e", 2012: "us2012e", 2013: "us2013e",
        2014: "us2014c", 2015: "us2015c", 2016: "us2016c", 2017: "us2017c", 2018: "us2018c",
        2019: "us2019c", 2020: "us2020c", 2021: "us2021c", 2022: "us2022c", 2023: "us2023c"
    }
    return mapping.get(year)

def get_state_fip(state_abbr):
    """
    Get the FIPS code for a U.S. state abbreviation.

    Parameters:
        state_abbr (str): Two-letter state abbreviation (e.g., 'FL').

    Returns:
        str: Two-digit FIPS code (e.g., '12'), or None if not found.
    """
    mapping = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10",
        "DC": "11", "FL": "12", "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18", "IA": "19",
        "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26", "MN": "27",
        "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35",
        "NY": "36", "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
        "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53",
        "WV": "54", "WI": "55", "WY": "56"
    }
    return mapping.get(state_abbr.upper())

def fetch_ipums_data_api(config):
    """
    Download IPUMS microdata via the IPUMS API and return it as a pandas DataFrame.

    Parameters:
        config (dict): The updated state config

    Returns:
        pd.DataFrame: Loaded microdata.

    Raises:
        ValueError: If the year is out of range.
        RuntimeError: If critical steps fail.
    """
    api_token = config["api_settings"].get("ipums_api_token")
    if not api_token:
        logging.error("IPUMS API token not provided in configuration.")
        return None

    ipums = IpumsApiClient(api_token)

    required_vars = [
    # geography & identifiers
    "PUMA", "STATEFIP", "COUNTYICP", "GQTYPE",
    # income
    "HHINCOME", "FTOTINC", "INCWAGE", "INCSS", "INCWELFR",
    "INCINVST", "INCRETIR", "INCSUPP", "INCEARN", "INCOTHER",
    # weights
    "HHWT",            # if you ever need the person weight
    "FAMUNIT",         # family identifier
    "CBSERIAL",        # household identifier
    # household & family
    "FAMSIZE", "NCHILD", "HHTYPE", "OWNERSHP", "MORTGAGE", 
    "MARST", "NFAMS", 
    # person & head selection
    "RELATE", "SEX", "AGE",
    # race & ethnicity
    "RACE", "HISPAN",
    # citizenship
    "CITIZEN",
    # veteran
    "VETSTAT",
    # disability
    "DIFFSENS",  # hearing/vision
    "DIFFPHYS",  # ambulatory
    "DIFFREM",   # cognitive
    "DIFFMOB",   # independent living
    # education & employment
    "EDUCD", "EMPSTAT",
]
    
    additional = config.get("additional_ipums_vars", "")
    variables = required_vars + [v.strip() for v in additional.split(",") if v.strip()]

    try:
        sample_code = get_ipums_sample_code(int(config["year"]))
    except ValueError as ve:
        logging.error(str(ve))
        return None

    extract = MicrodataExtract(
        collection="usa",
        description=f"5-year ACS extract for {config['state']} {config['year']}",
        samples=[sample_code],
        variables=variables
    )

    fip_code = get_state_fip(config["state"])
    if not fip_code:
        logging.error(f"Invalid state abbreviation: {config['state']}")
        return None

    try:
        extract.select_cases("STATEFIP", [fip_code])
        ipums.submit_extract(extract)
        ipums.wait_for_extract(extract)
        logging.info(f"Extract {extract.extract_id} completed.")
    except Exception as e:
        logging.error(f"Extract failure: {e}")
        return None

    download_dir = Path(config["api_settings"].get("download_dir", "api_downloads"))
    download_dir.mkdir(parents=True, exist_ok=True)

    try:
        ipums.download_extract(extract, download_dir=download_dir)
    except Exception as e:
        logging.error(f"Download failed: {e}")
        return None

    ddi_files = list(download_dir.glob("*.xml"))
    if not ddi_files:
        logging.error("No DDI file found.")
        return None

    try:
        ddi = readers.read_ipums_ddi(ddi_files[0])
    except Exception as e:
        logging.error(f"Failed to load DDI: {e}")
        return None

    data_path = download_dir / ddi.file_description.filename
    if not data_path.exists():
        gz_path = data_path.with_suffix(data_path.suffix + ".gz")
        if gz_path.exists():
            try:
                with gzip.open(gz_path, 'rb') as f_in, open(data_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            except Exception as e:
                logging.error(f"Decompression error: {e}")
                return None
        else:
            logging.error(f"Data file missing: {data_path}")
            return None

    try:
        df = readers.read_microdata(ddi, data_path)
        logging.info(f"Loaded IPUMS data with shape {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Failed to read microdata: {e}")
        return None
