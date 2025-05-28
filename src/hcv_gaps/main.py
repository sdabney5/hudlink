"""
Main script to process Housing Choice Voucher (HCV) eligibility data.

It delegates processing to the state_processor module, 
which loops over all states and years specified in the configuration.
"""
import logging
import time

from .state_processor import process_all_states
from .config import CONFIG


if __name__ == "__main__":
    start = time.perf_counter()
    process_all_states(CONFIG)
    elapsed = time.perf_counter() - start
    logging.info(f"💡 Total HCV gap run took {elapsed:.1f} seconds")
    
