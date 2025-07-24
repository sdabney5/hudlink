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
import time
import sys



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


def colored_text(text, color):
    """Return colored text with ANSI codes."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m', 
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m'
    }
    reset = '\033[0m'
    return f"{colors.get(color, '')}{text}{reset}"




def show_processing_spinner(stop_event):
    """Display a processing spinner while data is being processed."""
    spinner = [
        "●         ",
        " ●        ",
        "  ●       ",
        "   ●      ",
        "    ●     ",
        "     ●    ",
        "      ●   ",
        "       ●  ",
        "        ● ",
        "         ●",
        "        ● ",
        "       ●  ",
        "      ●   ",
        "     ●    ",
        "    ●     ",
        "   ●      ",
        "  ●       ",
        " ●        ",
    ]
    message = "hudlink is processing your data"
    
    # Hide cursor
    print("\033[?25l", end="", flush=True)
    
    try:
        i = 0
        while not stop_event.is_set():
            # Clear line and rewrite spinner (handles interruptions better)
            print(f"\033[2K\r{message} {spinner[i % len(spinner)]}", end="", flush=True)
            time.sleep(0.1)  
            i += 1
    finally:
        # Always restore cursor even if something goes wrong
        print("\033[?25h", end="", flush=True)  # Show cursor
        print("\033[2K", end="")  # Clear the line
        print("\r", end="")       # Return to start
        sys.stdout.flush()
        
        
        
def show_progress_dots(message, duration, stop_event):
    """Show message with fast animated dots for specified duration."""
    cycles_per_second = 4  # Complete 0->1->2->3 cycle 4 times per second
    total_cycles = duration * cycles_per_second
    
    # Hide cursor
    print("\033[?25l", end="", flush=True)
    
    try:
        for i in range(total_cycles):
            if stop_event.is_set():
                break
            dots = "." * ((i % 3) + 1)  # Cycles through 1, 2, 3 dots
            # Clear entire line, then show message with dots
            print(f"\033[2K\r{message}{dots}", end="", flush=True)
            time.sleep(0.25)  # 4 times per second (1/4 = 0.25)
    finally:
        # Always restore cursor and clear line
        print("\033[?25h", end="", flush=True)
        print("\033[2K\r", end="", flush=True)



def show_waiting_messages(stop_event):
    """Display rotating messages with animated dots."""
    messages = [

        "hudlink is getting your ACS data from IPUMS",
        "This may take a few minutes",
        "Thanks for your patience"
        ]
    while not stop_event.is_set():
        for msg in messages:
            if stop_event.is_set():
                break
            show_progress_dots(msg, 10, stop_event)
            if not stop_event.is_set():
                time.sleep(0.5)
        
                
def show_download_messages(stop_event):
    """Display download progress messages with animated dots."""
    messages = [
        "Downloading IPUMS extract",
        "This may take a minute",
    ]
    while not stop_event.is_set():
        for msg in messages:
            if stop_event.is_set():
                break
            show_progress_dots(msg, 9, stop_event)
            if not stop_event.is_set():
                time.sleep(0.5)
                
def show_success_message(message):
    """Display a success message with proper line clearing."""
    print("\033[2K\r")  
    print()             
    print()             
    print("=" * 50)    
    print()
    print(f" {message}")
    print()
    print("=" * 50)     
    print()           
    print()            

def expand_program_names(program_labels):
    """Convert program shortcuts to full names, works for both config and CLI."""
    if isinstance(program_labels, str):
        program_labels = [program_labels]
    
    expanded = []
    for prog in program_labels:
        prog_upper = prog.strip().upper()
        expanded.append(PROGRAM_SHORTCUTS.get(prog_upper, prog.strip()))
    
    return expanded
def show_hudlink_banner():
    """Display a welcome banner before processing."""
    # Hide cursor for cleaner display
    print("\033[?25l", end="", flush=True)
    
    try:
        # Display the logo
        for line in hudlink_logo:
            print(line)
        
        # Pause for 3 seconds
        time.sleep(3)
        
        # Clear the entire logo 
        for i in range(len(hudlink_logo)):
            print("\033[A\033[2K", end="")
        print("\r", end="", flush=True)
        
    finally:
        # Restore cursor
        print("\033[?25h", end="", flush=True)
    
    # Now show the rest of the banner normally
    print("\n"*5)
    print("_" * 48 + "\n" + "_" * 48 + "\n" * 5 )
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + " " * 10 + " Thanks for using hudlink! " + " " * 11 + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\n" + "If you use hudlink, please cite it:" + "\n" )
    print("Dabney, Shane. (2025). hudlink: Automated ACS-HUD") 
    print("data linking for housing analysis. Version 3.0.0" + "\n" *5)
def show_state_completion_message(state, year):
    """Display completion message for each state-year combination."""
    print("\n" + "─" * 50 + "\n")
    print(f"     hudlink successfully completed:  {state.upper()} {year}")
    print("\n" + "─" * 50 + "\n")

def show_hudlink_completion_banner():
    """Display a completion banner after all processing."""
    print("\n" * 3)
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + " " * 13 + "  hudlink sucessful!  " + " " * 13 + "║")
    print("║" + " " * 48 + "║")
    print("║" + " " * 5 + " Check your output folder for results " + " " * 5 + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\n" + "If you use hudlink, please cite it:" + "\n")
    print("Dabney, Shane. (2025). hudlink: Automated ACS-HUD") 
    print("data linking for housing analysis. Version 3.0.0" + "\n" *3)
    print("_________")
    print("Data sources (please cite in publications):")
    print("  • IPUMS USA, University of Minnesota, www.ipums.org")
    print("       See: https://usa.ipums.org/usa/cite.shtml ") 
    print("  • U.S. Census Bureau, American Community Survey")  
    print("  • HUD Picture of Subsidized Housing & Income Limits")
    print("  • MCDC Geocorr crosswalk data")
    print("\n" * 2)
    
def show_temporary_message(message, duration=3, clear_line_first=True):
    """
    Display a temporary message that disappears after a specified duration.
    
    Parameters:
        message (str): Message to display
        duration (float): How long to show the message in seconds (default: 3)
        clear_line_first (bool): Whether to clear the current line first (default: True)
    """
    # Hide cursor for cleaner display
    print("\033[?25l", end="", flush=True)
    
    try:
        # Optionally clear current line first
        if clear_line_first:
            print("\033[2K\r", end="", flush=True)
        
        # Show the message
        print(message, end="", flush=True)
        
        # Wait for specified duration
        time.sleep(duration)
        
    finally:
        # Clear the message and restore cursor
        print("\033[2K\r", end="", flush=True)  # Clear the line
        print("\033[?25h", end="", flush=True)  # Show cursor




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


def show_income_aggregation_warning(state, agg_method):
    """
    Display warning for multiple income limit values requiring aggregation.
    
    Parameters:
        state (str): State abbreviation
        agg_method (str): Aggregation method being used
    """
    print("\033[2K\r", end="", flush=True)
    print()
    print(colored_text("─" * 90, "yellow"))
    print(colored_text("─" * 90, "yellow"))
    print()
    print(f"     hudlink found multiple HUD income limit values for some {state.upper()} counties.")
    print(f" ⚠️  Consolidating using '{agg_method}' method (taking the {agg_method} value per county).")
    print("      You can change the aggregation method to [min|max|median|mean] if preferred.")
    print()
    print(colored_text("─" * 90, "yellow"))
    print(colored_text("─" * 90, "yellow"))
    print()


def show_CT_warning():
    """
    Display warning for most recent CT county Equivalents
    """
    print("\033[2K\r", end="", flush=True)
    print()
    print(colored_text("_" * 90, "yellow"))
    print(colored_text("_" * 90, "yellow"))
    print()
    print("     hudlink detected Connecticut 2023 data with new county equivalents.")
    print("     As of 2025, geocorr crosswalk data doesn't yet support CT's new county structure.")
    print(" ⚠️  hudlink uses a custom PUMA-to-county mapping as a workaround.")
    print("     This may result in some geographic irregularities - use outputs carefully.")
    print("     hudlink will update to official crosswalks when geocorr releases them.")
    print()
    print(colored_text("_" * 90, "yellow"))
    print(colored_text("_" * 90, "yellow"))
    print()

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




















hudlink_logo = [
"                                                                                      ",
"                                         ####                                         ",
"                                       ###  ###                                       ",
"                                     ###      ###                                     ",
"                                  ###            ###                                  ",
"                                ###      ####      ###                                ",
"                             ###      ##########      ###                             ",
"                           ###      ##############      ###                           ",
"                         ##       ##################       ##                         ",
"                      ###      ########################      ###                      ",
"                    ###      ############################       ##                    ",
"                           ################################                           ",
"                         ####################################                         ",
"                         ####################################                         ",
"                         ####################################                         ",
"                         ####################################                         ",
"                         ####################################                         ",
"                         ####################################                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                         ############            ############                         ",
"                                                                                      ",
"                                                                                      ",
"       #                                #    ##     #                 ##              ",
"       #                                #    ##                       ##              ",
"       ##  ##       #     #        ###  #    ##     #     #  ###      ##    ##        ",
"       ##    ##     #     #     ##     ##    ##     #     ##    #     ##  ##          ",
"       #      #     #     #     #       #    ##     #     #     ##    #####           ",
"       #      #     #     #     ##     ##    ##     #     #     ##    ##  ##          ",
"       ##     #     #######      ########    ##     #     #     ##    ##   ###        ",
"                                                                                      "    
]