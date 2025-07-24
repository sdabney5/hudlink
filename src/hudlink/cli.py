"""

Command-line interface for hudlink housing analysis.

This module provides a comprehensive command-line interface for the hudlink package,
allowing users to analyze housing subsidy eligibility and allocation patterns without
editing configuration files. The CLI supports all major configuration options and
provides helpful utilities for program discovery and validation.

The interface is designed for both quick analyses and complex research workflows,
with sensible defaults from the configuration file and the ability to override any
setting via command-line arguments.

Key Features:
    - Override any configuration setting from the command line
    - Use program shortcuts (HCV, PH, ALL) or full program names
    - Built-in help system with examples and program listings
    - Input validation with helpful error messages  
    - Verbose logging support for debugging
    - Backwards compatible with existing config.py workflows

Examples:
    Basic usage with config file defaults:
        $ hudlink

    Analyze specific states and years:
        $ hudlink --states FL,CA --years 2023

    Use program shortcuts with verbose output:
        $ hudlink -s TX -p HCV,PH --verbose

    Advanced analysis options:
        $ hudlink -s NY -y 2022,2023 --split-families --exclude-group-quarters

    Get help and program information:
        $ hudlink --help
        $ hudlink --list-programs

Functions:
    create_parser(): Creates and configures the argument parser with all options.
    list_available_programs(): Displays available HUD programs and shortcuts.
    parse_and_validate_args(args): Validates CLI arguments and returns config updates.
    main(): Main CLI entry point that processes arguments and runs analysis.


"""


import argparse
import logging
import sys
from .state_processor import process_all_states
from .config import CONFIG


def create_parser():
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog='hudlink',
        description='Automated ACS-HUD data linking for housing analysis',
        epilog='''
Examples:
  hudlink                                    # Use config.py settings
  hudlink -s FL,CA -y 2023                  # Analyze FL and CA for 2023
  hudlink --states TX --programs HCV,PH     # Texas with specific programs
  hudlink -s NY -y 2022,2023 --verbose      # Multiple years with verbose output
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Core analysis options
    parser.add_argument(
        '--states', '-s',
        help='Comma-separated state abbreviations (e.g., FL,CA,TX)',
        metavar='STATES'
    )
    
    parser.add_argument(
        '--years', '-y',
        help='Comma-separated years for ACS data (e.g., 2022,2023)',
        metavar='YEARS'
    )
    
    parser.add_argument(
        '--programs', '-p',
        help='Comma-separated HUD programs to analyze. Use shortcuts like HCV,PH,ALL or full names',
        metavar='PROGRAMS'
    )
    
    # Processing options
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory for results',
        metavar='PATH'
    )
    
    parser.add_argument(
        '--split-families',
        action='store_true',
        help='Analyze at family level instead of household level'
    )
    
    parser.add_argument(
        '--exclude-group-quarters',
        action='store_true',
        help='Exclude group quarters (institutional populations) from analysis'
    )
    
    parser.add_argument(
        '--no-race-sampling',
        action='store_true',
        help='Disable race-based incarceration adjustments'
    )
    
    # Utility options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--list-programs',
        action='store_true',
        help='List available HUD programs and shortcuts, then exit'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 3.0.0'
    )
    
    return parser


def list_available_programs():
    """Display available HUD programs and shortcuts."""
    from .file_utils import PROGRAM_SHORTCUTS
    
    print("Available HUD Programs:")
    print("=" * 50)
    print("\nFull Program Names:")
    unique_programs = set(PROGRAM_SHORTCUTS.values())
    for program in sorted(unique_programs):
        print(f"  • {program}")
    
    print("\nShortcuts:")
    for shortcut, full_name in sorted(PROGRAM_SHORTCUTS.items()):
        print(f"  {shortcut:12} → {full_name}")
    
    print("\nExample usage:")
    print("  hudlink --programs HCV,PH")
    print("  hudlink --programs 'Housing Choice Vouchers,Public Housing'")


def parse_and_validate_args(args):
    """Parse and validate command line arguments."""
    config_updates = {}
    
    if args.states:
        states = [s.strip().upper() for s in args.states.split(',')]
        # Basic validation - could be expanded
        invalid_states = [s for s in states if len(s) != 2]
        if invalid_states:
            print(f"Warning: These don't look like valid state codes: {invalid_states}")
        config_updates['states'] = [s.lower() for s in states]  # Convert back to lowercase for templates
    
    if args.years:
        try:
            years = [int(y.strip()) for y in args.years.split(',')]
            # Basic year validation
            invalid_years = [y for y in years if y < 2009 or y > 2025]
            if invalid_years:
                print(f"Warning: These years may not have ACS data available: {invalid_years}")
            config_updates['ipums_years'] = years
        except ValueError:
            print("Error: Invalid year format. Use comma-separated integers (e.g., 2022,2023)")
            sys.exit(1)
    
    if args.programs:
        programs = [p.strip() for p in args.programs.split(',')]
        config_updates['program_labels'] = programs  # Will be expanded by state_processor
    
    if args.output_dir:
        config_updates['output_directory'] = args.output_dir
    
    if args.split_families:
        config_updates['split_households_into_families'] = True
    
    if args.exclude_group_quarters:
        config_updates['exclude_group_quarters'] = True
    
    if args.no_race_sampling:
        config_updates['race_sampling'] = False
    
    if args.verbose:
        config_updates['verbose'] = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    return config_updates


def main():
    """
    Main entry point supporting both configuration file and CLI usage.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle special cases
    if args.list_programs:
        list_available_programs()
        return
    
    # Set up logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO
    )
    
    # Start with base config, apply CLI overrides
    config = CONFIG.copy()
    cli_updates = parse_and_validate_args(args)
    config.update(cli_updates)
    
    # Display what will be processed
    if cli_updates or args.verbose:
        print("hudlink Configuration:")
        print(f"  States: {config['states']}")
        print(f"  Years: {config['ipums_years']}")
        print(f"  Programs: {config['program_labels']}")
        print(f"  Output: {config['output_directory']}")
        print()
    
    # Run the analysis
    logging.info("Starting hudlink eligibility data processing.")
    try:
        process_all_states(config)
        logging.info("Completed hudlink eligibility data processing.")
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        if args.verbose:
            raise  # Show full traceback in verbose mode
        sys.exit(1)


if __name__ == "__main__":
    main()