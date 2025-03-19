"""
Main script to process Housing Choice Voucher (HCV) eligibility data.

It delegates the processing to the state_processor module, 
which loops over all states specified in the configuration.
"""

from .state_processor import process_all_states
from .config import CONFIG

if __name__ == "__main__":
    process_all_states(CONFIG)
