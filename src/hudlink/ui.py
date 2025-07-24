# -*- coding: utf-8 -*-
"""
User Interface and Display Functions for hudlink.

This module handles all terminal output formatting, banners, warnings,
spinners, and other user-facing display elements.

"""
import time
import sys

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



def show_income_aggregation_warning(state, agg_method):
    """Display warning for multiple income limit values requiring aggregation."""
    print("\033[2K\r", end="", flush=True)  # Clear current line
    print("\033[2K\r")
    print("\033[2K\r" + colored_text("─" * 90, "yellow"))
    print("\033[2K\r" + colored_text("─" * 90, "yellow"))
    print("\033[2K\r")
    print("\033[2K\r" + f"     hudlink found multiple HUD income limit values for some {state.upper()} counties.")
    print("\033[2K\r" + f" ⚠️  Consolidating using '{agg_method}' method (taking the {agg_method} value per county).")
    print("\033[2K\r" + "     You can change this in the config or with --agg-method [min|max|median|mean] if preferred.")
    print("\033[2K\r")
    print("\033[2K\r" + colored_text("─" * 90, "yellow"))
    print("\033[2K\r" + colored_text("─" * 90, "yellow"))
    print("\033[2K\r")
    
    
def show_CT_warning():
    """
    Display warning for most recent CT county Equivalents
    """
    print("\033[2K\r", end="", flush=True)
    print("\033[2K\r")
    print("\033[2K\r" + colored_text("_" * 90, "yellow"))
    print("\033[2K\r" + colored_text("_" * 90, "yellow"))
    print("\033[2K\r")
    print("\033[2K\r" + "     hudlink detected Connecticut 2023 data with new county equivalents.")
    print("\033[2K\r" + "     As of 2025, geocorr crosswalk data doesn't yet support CT's new county structure.")
    print("\033[2K\r" + " ⚠️  hudlink uses a custom PUMA-to-county mapping as a workaround.")
    print("\033[2K\r" + "     This may result in some geographic irregularities - use outputs carefully.")
    print("\033[2K\r" + "     hudlink will update to official crosswalks when geocorr releases them.")
    print("\033[2K\r")
    print("\033[2K\r" + colored_text("_" * 90, "yellow"))
    print("\033[2K\r" + colored_text("_" * 90, "yellow"))
    print("\033[2K\r")
    
    
    
    
    









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
"       ## ###       #     #        ###  #    ##     #     #  ###      ##    ##        ",
"       #     ##     #     #     ##     ##    ##     #     ##    #     ##  ##          ",
"       #      #     #     #     #       #    ##     #     #     ##    #####           ",
"       #      #     #     #     ##     ##    ##     #     #     ##    ##  ##          ",
"       #      #     #######      ########    ##     #     #      #    ##   ###        ",
"                                                                                      "    
]