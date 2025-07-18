"""
Main entry point for processing and producing hudlink data.

Delegates the task to the `state_processor` module, which processes all states 
and years specified in the configuration (`CONFIG`).
"""

import logging
from .state_processor import process_all_states
from .config import CONFIG

def main():
    """
    Called by the console‐script entry. Sets up logging and runs the pipeline.
    """
    logging.info("Starting hudlink eligibility data processing.")
    process_all_states(CONFIG)
    logging.info("Completed hudlink eligibility data processing.")

if __name__ == "__main__":
    main()
