"""
Main entry point for hudlink housing analysis package.

This module serves as the primary entry point for the hudlink package, delegating
to the command-line interface module for argument parsing and user interaction.
The module maintains backwards compatibility with direct imports while providing
a clean separation between the CLI interface and core processing logic.

The main() function is called by the console script entry point defined in
pyproject.toml, allowing users to run 'hudlink' from the command line after
installation. All user interface logic, argument parsing, and configuration
management is handled by the cli module.

Entry Points:
    Console script: 'hudlink' command after pip installation
    Direct import: Can be imported and called programmatically
    Module execution: python -m hudlink.main

Author: Shane Dabney
"""

from .cli import main

if __name__ == "__main__":
    main()