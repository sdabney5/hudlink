"""
File Utilities Module for hudlink.

This module provides utility functions for:
- Creating standardized output directories for each state-year combo.
- Cleaning and formatting eligibility and summary DataFrames.
- Managing the IPUMS API token from a plain-text file.
- Clearing cached API downloads.
"""

import os
import logging
import shutil
from pathlib import Path
from .ui import show_CT_warning



# Config program-name shortcut dict
PROGRAM_SHORTCUTS = {
    'HCV': 'Housing Choice Vouchers',
    'PH': 'Public Housing', 
    'LIHTC': 'LIHTC',
    'ALL': 'Summary of All HUD Programs',
    'S8': 'Housing Choice Vouchers',
    'VOUCHERS': 'Housing Choice Vouchers',
    'S236': 'Section 236',
    'S8NC': 'Section 8 NC/SR', 
    'S8SR': 'Section 8 NC/SR',
    '811': '811/PRAC',
    '202': '202/PRAC',
    'PRAC': '811/PRAC',
    'MF': 'Multi-Family Other',
    'MODR': 'Mod Rehab',
}


def expand_program_names(program_labels):
    """Convert program shortcuts to full names, works for both config and CLI."""
    if isinstance(program_labels, str):
        program_labels = [program_labels]
    
    expanded = []
    for prog in program_labels:
        prog_upper = prog.strip().upper()
        expanded.append(PROGRAM_SHORTCUTS.get(prog_upper, prog.strip()))
    
    return expanded



def create_output_structure(root_output, state, year):
    """
    Create the output directory structure for a given state and year.

    Structure:
        root_output/
            STATE/
                STATE_YEAR/

    Parameters:
        root_output (str): Base output directory path.
        state (str): State abbreviation (e.g., 'FL').
        year (int or str): Year to process.

    Returns:
        str: Full path to the created output subdirectory.
    """
    if not os.path.exists(root_output):
        os.makedirs(root_output)
        logging.info(f"Created root output directory: {root_output}")

    state_dir = os.path.join(root_output, state.upper())
    if not os.path.exists(state_dir):
        os.makedirs(state_dir)
        logging.info(f"Created state directory: {state_dir}")

    final_dir = os.path.join(state_dir, f"{state.upper()}_{year}")
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)
        logging.info(f"Created output directory for {state.upper()} {year}: {final_dir}")

    return final_dir


def get_default_output_directory():
    """
    Return the default output directory path on the user's Desktop.

    Returns:
        str: Path to ~/Desktop/hudlink_output
    """
    # Try OneDrive Desktop first, then regular Desktop
    user_dir = os.path.expanduser("~")
    onedrive_desktop = os.path.join(user_dir, "OneDrive", "Desktop")
    regular_desktop = os.path.join(user_dir, "Desktop")
    
    if os.path.exists(onedrive_desktop):
        desktop = onedrive_desktop
    else:
        desktop = regular_desktop
        
    return os.path.join(desktop, "hudlink_output")


    
def clean_eligibility_df(elig_df, state, year):
    """
    Clean eligibility DataFrame by removing unnecessary columns and correcting county labels.

    - Drops 'State abbr.' column if present.
    - For CT 2023 only: maps PUMAs to new Planning Region names.

    Parameters:
        elig_df (pd.DataFrame): Raw eligibility data.
        state (str): State abbreviation.
        year (int | str): Year to process.

    Returns:
        pd.DataFrame: Cleaned eligibility DataFrame.
    """
    df = elig_df.drop(columns=["State abbr."], errors="ignore").copy()

    if state == "CT" and int(year) == 2023:
        show_CT_warning()

        ct_puma_to_county = {
            "20100": "Northwest Hills Planning Region CT",
            "20201": "Capitol Planning Region CT",
            "20202": "Lower Connecticut River Valley Planning Region CT",
            "20203": "Capitol Planning Region CT",
            "20204": "Capitol Planning Region CT",
            "20205": "Capitol Planning Region CT",
            "20206": "Capitol Planning Region CT",
            "20207": "Capitol Planning Region CT",
            "20301": "Northeastern Connecticut Planning Region CT",
            "20401": "Southeastern Connecticut Planning Region CT",
            "20402": "Southeastern Connecticut Planning Region CT",
            "20500": "Lower Connecticut River Valley Planning Region CT",
            "20601": "South Central Connecticut Planning Region CT",
            "20602": "South Central Connecticut Planning Region CT",
            "20603": "South Central Connecticut Planning Region CT",
            "20604": "South Central Connecticut Planning Region CT",
            "20701": "Naugatuck Valley Planning Region CT",
            "20702": "Naugatuck Valley Planning Region CT",
            "20703": "Naugatuck Valley Planning Region CT",
            "20801": "Greater Bridgeport Planning Region CT",
            "20802": "Greater Bridgeport Planning Region CT",
            "20901": "Western Connecticut Planning Region CT",
            "20902": "Western Connecticut Planning Region CT",
            "20903": "Western Connecticut Planning Region CT",
            "20904": "Western Connecticut Planning Region CT"
        }

        if "PUMA" in df.columns:
            df["County_Name"] = df.apply(
                lambda r: ct_puma_to_county.get(str(r["PUMA"]), r["County_Name"]),
                axis=1,
            )

    return df


def tidy_summary_df(summary_df, state):
    """
    Tidy the final summary DataFrame by dropping and renaming columns.
    - For AK and LA: removes trailing ' County' from County_Name values

    Parameters:
        summary_df (pd.DataFrame): Summary statistics table.
        state (str): State abbreviation.

    Returns:
        pd.DataFrame: Tidy summary DataFrame.
    """
    df = summary_df.drop(columns=["Name", "% Minority_x"], errors="ignore")
    df = df.rename(columns={"% Minority_y": "% Minority"}, errors="ignore")

    if state in {"AK", "LA"} and "County_Name" in df.columns:
        df["County_Name"] = df["County_Name"].str.replace(r"\s+County$", "", regex=True)

    return df


def load_ipums_api_token(path):
    """
    Load the IPUMS API token from a plain text file.

    Parameters:
        path (str): Path to the token file.

    Returns:
        str: API token string.

    Raises:
        FileNotFoundError: If the token file does not exist.
        ValueError: If the file is empty or contains only whitespace.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing IPUMS API token file at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        token = f.read().strip()

    if not token:
        raise ValueError(f"IPUMS API token file at {path} is empty.")

    return token


def clear_api_downloads(folder):
    """
    Remove all files and subfolders inside the given API downloads folder.

    The folder itself is preserved.

    Parameters:
        folder (str | Path): Path to the API download directory.
    """
    folder = Path(folder)
    if not folder.exists():
        return

    for item in folder.iterdir():
        try:
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        except Exception as exc:
            logging.warning("Could not delete %s: %s", item, exc)


