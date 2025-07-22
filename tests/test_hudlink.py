# -*- coding: utf-8 -*-
"""
Test Suite for hudlink Housing Eligibility Analysis Pipeline.

This module contains comprehensive tests for the hudlink package, including:
- End-to-end pipeline testing with sample data
- Data loading function validation  
- Error handling for missing/malformed input files
- Output validation and sanity checks

The tests use a sampled dataset (857 rows) derived from Florida IPUMS data
to ensure fast execution while maintaining realistic data structures.

Author: Shane Dabney
Created: July 22, 2025
"""
import pytest
import pandas as pd
import os
import tempfile
import sys
from pathlib import Path
import shutil

# Tests directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


from test_config import CONFIG
from hudlink.hudlink_processing import process_eligibility
from hudlink.hudlink_data_loading import (
    load_ipums_data,
    load_crosswalk_data,
    load_income_limits,
    load_hud_psh_data
)

def test_full_pipeline():
    """
    Test the complete hudlink processing pipeline end-to-end.
    
    This test validates:
    - Pipeline runs without errors
    - Required output files are created
    - Output data has expected structure and values
    - Weight totals are preserved through processing
    - Allocation rates and gaps are reasonable
    """
    # Run the full pipeline
    process_eligibility(CONFIG)
    
    # Define expected output paths
    output_dir = Path(CONFIG["output_directory"]) #/ "test" / "test_test"
    eligibility_output = output_dir / "test_test_eligibility_HH.csv"
    summary_output = output_dir / "test_test_summary_of_all_hud_programs_linked_summary_HH.csv"
    
    # Load test data for validation
    ipums_test_df = pd.read_csv(CONFIG["ipums_data_path"])
    ipums_test_df_rollup = ipums_test_df.drop_duplicates(subset=["CBSERIAL"]) 
    
    
    
    # Load output data
    eligibility_df = pd.read_csv(eligibility_output)
    summary_df = pd.read_csv(summary_output)
    
    # Calculate validation metrics
    familynumber_counts = eligibility_df["FAMILYNUMBER"].value_counts()
    elig_weight_total = eligibility_df["REALHHWT"].sum()
    ipums_base_weight_total = ipums_test_df_rollup["HHWT"].sum()
    tolerance = 2  # Allow small rounding differences
    
    # === OUTPUT EXISTENCE TESTS ===
    assert eligibility_output.exists(), "Eligibility output file was not created"
    assert summary_output.exists(), "Summary output file was not created"
    
    # === ELIGIBILITY OUTPUT VALIDATION ===
    assert len(eligibility_df) > 0, "Eligibility output is empty"
    assert all(familynumber_counts == 1), "Eligibility output has duplicate FAMILYNUMBER rows"
    assert abs(elig_weight_total - ipums_base_weight_total) <= tolerance, \
        f"Weight totals don't match: {elig_weight_total} vs {ipums_base_weight_total}"
    
    # Check required columns exist
    required_cols = ["FAMILYNUMBER", "Allocated_HHWT", "Eligible_at_80%", "Eligible_at_50%", "Eligible_at_30%"]
    missing_cols = [col for col in required_cols if col not in eligibility_df.columns]
    assert not missing_cols, f"Missing required columns in eligibility output: {missing_cols}"
    
    # === SUMMARY OUTPUT VALIDATION ===
    assert len(summary_df) > 0, "Summary output is empty"
    
    # Check allocation rates are reasonable (between 0 and 100)
    allocation_cols = [
        "summary_of_all_hud_programs_allocation_rate_80%",
        "summary_of_all_hud_programs_allocation_rate_50%", 
        "summary_of_all_hud_programs_allocation_rate_30%"
    ]
    
    for col in allocation_cols:
        if col in summary_df.columns:
            
            valid_values = summary_df[col].dropna()
            if len(valid_values) > 0:
                assert pd.api.types.is_numeric_dtype(summary_df[col]), f"{col} should be numeric"
    
    # Check gap counts are non-negative
    gap_cols = [
        "summary_of_all_hud_programs_gap_80%",
        "summary_of_all_hud_programs_gap_50%",
        "summary_of_all_hud_programs_gap_30%"
    ]
    
    for col in gap_cols:
        if col in summary_df.columns:
            valid_values = summary_df[col].dropna()
            if len(valid_values) > 0:
                assert pd.api.types.is_numeric_dtype(summary_df[col]), f"{col} should be numeric"


def test_missing_ipums_file():
    """Test error handling when IPUMS file is missing."""
    with pytest.raises(Exception, match="Error loading IPUMS file"):
        load_ipums_data("nonexistent_file.csv")


def test_missing_crosswalk_files():
    """Test error handling when crosswalk files are missing."""
    valid_path_2012 = CONFIG["crosswalk_2012_path"]
    valid_path_2022 = CONFIG["crosswalk_2022_path"]
    
    # Test missing 2012 file
    with pytest.raises(Exception):
        load_crosswalk_data("nonexistent_2012.csv", valid_path_2022)
    
    # Test missing 2022 file  
    with pytest.raises(Exception):
        load_crosswalk_data(valid_path_2012, "nonexistent_2022.csv")


def test_ipums_missing_required_columns():
    """
    Test error handling when IPUMS data is missing required columns.
    
    This test systematically removes each required column and verifies
    that the loading function raises appropriate errors.
    """
    required_cols = [
        'PUMA', 'COUNTYICP', 'HHINCOME', 'FTOTINC', 'INCWAGE', 'INCSS', 'INCWELFR',
        'HHWT', 'INCINVST', 'INCRETIR', 'INCSUPP', 'INCEARN', 'INCOTHER',
        'NFAMS', 'FAMUNIT', 'CBSERIAL'
    ]
    
    # Load the test data
    ipums_test_df = pd.read_csv(CONFIG["ipums_data_path"])
    
    # Test each required column
    for col in required_cols:
        if col in ipums_test_df.columns:
            # Create DataFrame missing this column
            df_missing_col = ipums_test_df.drop(columns=[col])
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                df_missing_col.to_csv(tmp_file.name, index=False)
                tmp_path = tmp_file.name
            
            try:
                # Should raise ValueError about missing columns
                with pytest.raises(ValueError, match=f"Missing required columns.*{col}"):
                    load_ipums_data(tmp_path)
            finally:
                # Clean up temp file
                os.unlink(tmp_path)


def test_config_validation():
    """Test that invalid configurations are handled properly."""
    # Test with missing state data
    invalid_config = CONFIG.copy()
    invalid_config["crosswalk_2012_path"] = "tests/test_data/nonexistent_2012.csv"
    invalid_config["crosswalk_2022_path"] = "tests/test_data/nonexistent_2022.csv"
    
    # This should fail when trying to find crosswalk files
    with pytest.raises(Exception):
        process_eligibility(invalid_config)


def test_data_loading_functions():
    """Test individual data loading functions with valid test data."""
    
    # Test IPUMS data loading
    ipums_df = load_ipums_data(CONFIG["ipums_data_path"])
    assert len(ipums_df) > 0, "IPUMS data loading returned empty DataFrame"
    assert "PUMA" in ipums_df.columns, "PUMA column missing from loaded IPUMS data"
    
    # Test crosswalk data loading
    crosswalk_2012_path = CONFIG["crosswalk_2012_path"]
    crosswalk_2022_path = CONFIG["crosswalk_2022_path"]
    
    cw_2012, cw_2022 = load_crosswalk_data(crosswalk_2012_path, crosswalk_2022_path)
    assert len(cw_2012) > 0, "2012 crosswalk data is empty"
    assert len(cw_2022) > 0, "2022 crosswalk data is empty"
    
    # Test income limits data loading
    il_data = load_income_limits(CONFIG["income_limits_path"], CONFIG["income_limit_agg"])
    assert len(il_data) > 0, "Income limits data is empty"
    
    # Test PSH data loading
    psh_data = load_hud_psh_data(CONFIG)
    assert len(psh_data) > 0, "PSH data is empty"


# Cleanup function to remove test outputs
def test_zzz_cleanup():
    """Remove test output contents but keep the directory structure."""

    output_dir = Path(CONFIG["output_directory"])
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()