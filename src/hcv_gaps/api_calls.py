"""
API Calls Module for HCV Analysis.

This module provides functions to fetch IPUMS USA data via the IPUMS API using ipumspy.
It is designed to work with 5-year ACS data from the IPUMS USA collection. The module:
  - Constructs a MicrodataExtract object with a required set of variables (plus any additional ones specified in the configuration).
  - Applies state filtering using the state's FIPS code.
  - Submits the extract and waits for its completion.
  - Downloads the extract into a directory specified in the configuration.
  - Uses the downloaded DDI XML file to load the microdata into a pandas DataFrame via ipumspy's DDI-based readers.
  
Functions included:
  - get_ipums_sample_code(year): Returns the sample code corresponding to the specified year.
  - get_state_fip(state_abbr): Maps a state abbreviation (e.g., "FL") to its corresponding FIPS code.
  - fetch_ipums_data_api(config): Orchestrates the extract request, download, and data loading process, returning a DataFrame.

Usage Example:
    from api_calls import fetch_ipums_data_api
    config = {
         "state": "FL",
         "year": 2022,
         "api_settings": {
              "ipums_api_token": "<YOUR_API_TOKEN>",
              "download_dir": "data/api_downloads"
         },
         "additional_ipums_vars": "VAR1,VAR2"  # Optional: additional variables
    }
    df = fetch_ipums_data_api(config)
"""

import os
import logging
import gzip
import shutil
import pandas as pd
from io import StringIO
from datetime import datetime
from pathlib import Path
from ipumspy import IpumsApiClient, MicrodataExtract, readers  # Ensure ipumspy is installed

def get_ipums_sample_code(year):
    """
    Returns the appropriate sample code for 5-year ACS data for a given year.
    
    The supported years are 2009 through the current year.
    
    Parameters:
        year (int): The desired year.
        
    Returns:
        str: The corresponding sample code.
        
    Raises:
        ValueError: If the year is less than 2009 or greater than the current year.
    """
    current_year = datetime.now().year
    if year < 2009 or year > current_year:
        raise ValueError(f"Year must be between 2009 and {current_year}. Provided: {year}")
    mapping = {
        2009: "us2009e",
        2010: "us2010e",
        2011: "us2011e",
        2012: "us2012e",
        2013: "us2013e",
        2014: "us2014c",
        2015: "us2015c",
        2016: "us2016c",
        2017: "us2017c",
        2018: "us2018c",
        2019: "us2019c",
        2020: "us2020c",
        2021: "us2021c",
        2022: "us2022c",
        2023: "us2023c"
    }
    return mapping.get(year)

def get_state_fip(state_abbr):
    """
    Maps a state abbreviation to its corresponding FIPS code as used in IPUMS.
    
    Parameters:
        state_abbr (str): The state abbreviation (e.g., "FL").
    
    Returns:
        str: The corresponding FIPS code (e.g., "12") or None if not found.
    """
    mapping = {
        "AL": "01", "AK": "02", "AZ": "04", "AR": "05", "CA": "06",
        "CO": "08", "CT": "09", "DE": "10", "DC": "11", "FL": "12",
        "GA": "13", "HI": "15", "ID": "16", "IL": "17", "IN": "18",
        "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23",
        "MD": "24", "MA": "25", "MI": "26", "MN": "27", "MS": "28",
        "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33",
        "NJ": "34", "NM": "35", "NY": "36", "NC": "37", "ND": "38",
        "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44",
        "SC": "45", "SD": "46", "TN": "47", "TX": "48", "UT": "49",
        "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55",
        "WY": "56"
    }
    return mapping.get(state_abbr.upper(), None)

def fetch_ipums_data_api(config):
    """
    Fetch IPUMS USA data via the IPUMS API using ipumspy.
    
    Constructs a MicrodataExtract object for 5-year ACS data using a required set of variables,
    plus any additional variables specified in the configuration. It applies state filtering using the state's FIPS code,
    submits the extract, waits for its completion, downloads the data into a directory specified by 
    "download_dir" in the API settings, and then loads the data into a pandas DataFrame using ipumspy's DDI-based readers.
    
    If the downloaded extract includes a DDI XML file, that file is used to load the microdata.
    
    Parameters:
        config (dict): Configuration dictionary that must include:
            - "state": The state abbreviation (e.g., "FL").
            - "year": The desired year (e.g., 2019).
            - "api_settings": A dict with at least:
                  "ipums_api_token": Your IPUMS API token.
                  "download_dir": (Optional) The directory where the extract will be downloaded (defaults to "api_downloads").
            - (Optional) "additional_ipums_vars": A comma-separated string of extra variables.
    
    Returns:
        pd.DataFrame: A DataFrame containing the IPUMS microdata, or None if an error occurs.
    
    Raises:
        ValueError: If the specified year is not between 2009 and the current year.
    """
    # Retrieve the API token.
    api_token = config["api_settings"].get("ipums_api_token")
    if not api_token:
        logging.error("IPUMS API token not provided in configuration.")
        return None

    # Initialize the API client.
    ipums = IpumsApiClient(api_token)
    
    required_vars = ["PUMA", "STATEFIP", "COUNTYICP", "HHINCOME", "FTOTINC", "INCWAGE",
                     "INCSS", "INCWELFR", "HHWT", "INCINVST", "INCRETIR",
                     "INCSUPP", "INCEARN", "INCOTHER", "NFAMS", "FAMUNIT", "CBSERIAL", 
                     "AGE", "EDUCD", "EMPSTAT", "HHTYPE", "RACE", "RELATE", "VETSTAT", 
                     "FAMSIZE", "GQTYPE", "OWNERSHP"]
    additional_vars_str = config.get("additional_ipums_vars")
    if additional_vars_str:
        additional_vars = [var.strip() for var in additional_vars_str.split(",") if var.strip()]
        variables = required_vars + additional_vars
    else:
        variables = required_vars

    try:
        sample_code = get_ipums_sample_code(int(config["year"]))
    except ValueError as ve:
        logging.error(str(ve))
        return None
    samples = [sample_code]

    extract = MicrodataExtract(
        collection="usa",
        description=f"5-year ACS extract for state {config['state']} in {config['year']}",
        samples=samples,
        variables=variables
    )
    
    # Apply state filtering using the state's FIPS code.
    fip_code = get_state_fip(config["state"])
    if not fip_code:
        logging.error(f"Invalid state abbreviation: {config['state']}")
        return None
    try:
        extract.select_cases("STATEFIP", [fip_code])
        logging.info(f"Applied state filter: STATEFIP = {fip_code}")
    except Exception as e:
        logging.error(f"Error applying state filter: {e}")
        return None

    try:
        ipums.submit_extract(extract)
        logging.info(f"Submitted IPUMS extract with ID: {extract.extract_id}")
    except Exception as e:
        logging.error(f"Error submitting IPUMS extract: {e}")
        return None

    try:
        ipums.wait_for_extract(extract)
        logging.info(f"Extract {extract.extract_id} completed.")
    except Exception as e:
        logging.error(f"Error waiting for extract {extract.extract_id}: {e}")
        return None

    # Use the download directory from API settings.
    download_dir = Path(config["api_settings"].get("download_dir", "api_downloads"))
    download_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        ipums.download_extract(extract, download_dir=download_dir)
        logging.info(f"Extract {extract.extract_id} downloaded to {download_dir}")
    except Exception as e:
        logging.error(f"Error downloading extract {extract.extract_id}: {e}")
        return None

    # Locate the DDI file in the download directory.
    ddi_files = list(download_dir.glob("*.xml"))
    if not ddi_files:
        logging.error("No DDI file found in the download directory.")
        return None
    ddi_file = ddi_files[0]
    try:
        ddi = readers.read_ipums_ddi(ddi_file)
        logging.info(f"DDI file {ddi_file} loaded successfully.")
    except Exception as e:
        logging.error(f"Error reading DDI file {ddi_file}: {e}")
        return None

    # Determine the microdata file name from the DDI.
    data_filename = ddi.file_description.filename  # e.g., "usa_00024.dat"
    data_file = download_dir / data_filename
    if not data_file.exists():
        # If the uncompressed data file is not found, check for the gzipped file.
        gz_data_file = download_dir / (data_filename + ".gz")
        if gz_data_file.exists():
            logging.info(f"Found gzipped data file: {gz_data_file}. Decompressing...")
            try:
                with gzip.open(gz_data_file, 'rb') as f_in, open(data_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                logging.info(f"Decompressed file saved as: {data_file}")
            except Exception as e:
                logging.error(f"Error decompressing file {gz_data_file}: {e}")
                return None
        else:
            logging.error(f"Data file specified in DDI not found: {data_file}")
            return None

    try:
        ipums_df = readers.read_microdata(ddi, data_file)
        logging.info(f"IPUMS data loaded into DataFrame with shape {ipums_df.shape}")
        return ipums_df
    except Exception as e:
        logging.error(f"Error reading microdata: {e}")
        return None
