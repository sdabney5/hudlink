"""
hcv_final_outputs.py

This module contains functions to save the final HCV eligibility dataframe and to generate and save a summary
of eligibility counts for each county. Additionally, it can generate a more detailed summary including race statistics.

Functions:
1. extract_state_code_and_year(ipums_df):
    Extracts the state code and year from the IPUMS dataframe.

2. save_eligibility_dataframe(eligibility_df, output_dir):
    Saves the cleaned and processed IPUMS dataframe with eligibility status to a CSV file named with the state name and year.

3. calculate_voucher_gap_and_save(ipums_eligibility_df, hud_hcv_df, output_dir, display_race_stats=False):
    Creates a summary table of eligibility counts, subsidized units available, voucher gap,
    and percentage of eligible households for which vouchers are available by county.
    Optionally includes eligibility counts by race and relevant race recipient percentages if display_race_stats is True.
    Saves the summary table to a CSV file named with the state name and year.

Usage:
To use, import this module and call the functions with the appropriate dataframes.

Example:
    import hcv_final_outputs as hcv_outputs

    # Extract state code and year
    state_name, year = hcv_outputs.extract_state_code_and_year(ipums_df)

    # Save the eligibility dataframe
    hcv_outputs.save_eligibility_dataframe(ipums_df, output_dir)

    # Create and save the summary table
    hcv_outputs.calculate_voucher_gap_and_save(ipums_df, hud_hcv_df, output_dir, display_race_stats=True)
"""

# Imports
import os
import pandas as pd

def extract_state_code_and_year(ipums_df):
    """
    Extracts the state code and year from the IPUMS dataframe and maps it to the corresponding state name.

    Parameters:
    ----------
    ipums_df : pd.DataFrame
        The IPUMS dataframe containing the STATEICP and YEAR columns.

    Returns:
    -------
    tuple
        The state name corresponding to the state code in the dataframe and the year.

    Notes:
    -----
    - Uses a predefined mapping of state codes to state names.
    - Raises a ValueError if multiple or no state codes or years are found in the dataset.
    """
    state_mapping = {
        1: 'Connecticut', 2: 'Maine', 3: 'Massachusetts', 4: 'New Hampshire',
        5: 'Rhode Island', 6: 'Vermont', 11: 'Delaware', 12: 'New Jersey',
        13: 'New York', 14: 'Pennsylvania', 21: 'Illinois', 22: 'Indiana',
        23: 'Michigan', 24: 'Ohio', 25: 'Wisconsin', 31: 'Iowa', 32: 'Kansas',
        33: 'Minnesota', 34: 'Missouri', 35: 'Nebraska', 36: 'North Dakota',
        37: 'South Dakota', 40: 'Virginia', 41: 'Alabama', 42: 'Arkansas',
        43: 'Florida', 44: 'Georgia', 45: 'Louisiana', 46: 'Mississippi',
        47: 'North Carolina', 48: 'South Carolina', 49: 'Texas', 51: 'Kentucky',
        52: 'Maryland', 53: 'Oklahoma', 54: 'Tennessee', 56: 'West Virginia',
        61: 'Arizona', 62: 'Colorado', 63: 'Idaho', 64: 'Montana', 65: 'Nevada',
        66: 'New Mexico', 67: 'Utah', 68: 'Wyoming', 71: 'California', 72: 'Oregon',
        73: 'Washington', 81: 'Alaska', 82: 'Hawaii', 83: 'Puerto Rico', 96: 'State groupings (1980 Urban/rural sample)',
        97: 'Overseas Military Installations', 98: 'District of Columbia', 99: 'State not identified'
    }

    unique_state_code = ipums_df['STATEICP'].unique()
    if len(unique_state_code) == 1:
        state_code = unique_state_code[0]
    else:
        raise ValueError("Multiple or no state codes found in the dataset.")

    state_name = state_mapping.get(state_code, 'Unknown_State')

    unique_year = ipums_df['YEAR'].unique()
    if len(unique_year) == 1:
        year = unique_year[0]
    else:
        raise ValueError("Multiple or no years found in the dataset.")

    return state_name, year

def save_eligibility_dataframe(eligibility_df, output_dir):
    """
    Saves the eligibility dataframe to a CSV file named with the state name and year.

    Parameters:
    ----------
    eligibility_df : pd.DataFrame
        The cleaned and processed IPUMS dataframe with eligibility status.
    output_dir : str
        The directory where the output file should be saved.

    Returns:
    -------
    None

    Notes:
    -----
    - Extracts the state name and year using `extract_state_code_and_year` function.
    """
    state_name, year = extract_state_code_and_year(eligibility_df)
    file_name = f"{state_name}_{year}_eligibility.csv"
    file_path = os.path.join(output_dir, file_name)

    try:
        eligibility_df.to_csv(file_path, index=False)
        print(f"Unaggregated Eligibility dataframe saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def calculate_voucher_gap_and_save(ipums_eligibility_df, hud_hcv_df, output_dir, display_race_stats=False):
    """
    Calculates the voucher gap and HCV allocation rate for each county and optionally displays race stats.

    Parameters:
    ----------
    ipums_eligibility_df : pd.DataFrame
        The IPUMS eligibility dataframe.
    hud_hcv_df : pd.DataFrame
        The HUD HCV dataframe.
    output_dir : str
        The directory where the output file should be saved.
    display_race_stats : bool, optional
        If True, include race statistics in the output (default is False).

    Returns:
    -------
    None

    Notes:
    -----
    - Summarizes the eligibility data by county and merges it with HUD HCV data.
    - Calculates the voucher gap and HCV allocation rate at each threshold.
    - Optionally adds race statistics to the summary.
    - Saves the summary dataframe to a CSV file named with the state name and year.
    """
    def add_race_stats(df, hud_hcv_df):
        # Merge with HUD HCV data to get race stats
        df = df.merge(hud_hcv_df[['Name', '% Minority', '%White Non-Hispanic']],
                      left_on='County_Name', right_on='Name', how='left')

        # Add weighted counts for minorities and whites
        df['Weighted_Minority_Count_30%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_Minority_HH_Eligibility_Count_30%'].sum().values
        df['Weighted_White_Count_30%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_White_HH_Eligibility_Count_30%'].sum().values

        df['Weighted_Minority_Count_50%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_Minority_HH_Eligibility_Count_50%'].sum().values
        df['Weighted_White_Count_50%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_White_HH_Eligibility_Count_50%'].sum().values

        df['Weighted_Minority_Count_80%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_Minority_HH_Eligibility_Count_80%'].sum().values
        df['Weighted_White_Count_80%'] = ipums_eligibility_df.groupby('County_Name')['Weighted_White_HH_Eligibility_Count_80%'].sum().values

        # Calculate percentages of eligible households that are minority and white at each threshold
        df['% Eligible Minority at 30%'] = (df['Weighted_Minority_Count_30%'] / df['Weighted_Eligibility_Count_30%']) * 100
        df['% Eligible White at 30%'] = (df['Weighted_White_Count_30%'] / df['Weighted_Eligibility_Count_30%']) * 100

        df['% Eligible Minority at 50%'] = (df['Weighted_Minority_Count_50%'] / df['Weighted_Eligibility_Count_50%']) * 100
        df['% Eligible White at 50%'] = (df['Weighted_White_Count_50%'] / df['Weighted_Eligibility_Count_50%']) * 100

        df['% Eligible Minority at 80%'] = (df['Weighted_Minority_Count_80%'] / df['Weighted_Eligibility_Count_80%']) * 100
        df['% Eligible White at 80%'] = (df['Weighted_White_Count_80%'] / df['Weighted_Eligibility_Count_80%']) * 100

        return df

    # Summarize the eligibility data by county
    summary_df = ipums_eligibility_df.groupby('County_Name').agg({
        'Weighted_Eligibility_Count_30%': 'sum',
        'Weighted_Eligibility_Count_50%': 'sum',
        'Weighted_Eligibility_Count_80%': 'sum'
    }).reset_index()

    # Merge with HUD HCV data to get the number of subsidized units available
    summary_df = summary_df.merge(hud_hcv_df[['Name', 'Subsidized units available']],
                                  left_on='County_Name', right_on='Name', how='left')

    # Calculate the voucher gap at each threshold
    summary_df['Voucher_Gap_30%'] = summary_df['Weighted_Eligibility_Count_30%'] - summary_df['Subsidized units available']
    summary_df['Voucher_Gap_50%'] = summary_df['Weighted_Eligibility_Count_50%'] - summary_df['Subsidized units available']
    summary_df['Voucher_Gap_80%'] = summary_df['Weighted_Eligibility_Count_80%'] - summary_df['Subsidized units available']

    # Calculate the HCV allocation rate at each threshold
    summary_df['HCV_Allocation_Rate_30%'] = (summary_df['Subsidized units available'] / summary_df['Weighted_Eligibility_Count_30%']) * 100
    summary_df['HCV_Allocation_Rate_50%'] = (summary_df['Subsidized units available'] / summary_df['Weighted_Eligibility_Count_50%']) * 100
    summary_df['HCV_Allocation_Rate_80%'] = (summary_df['Subsidized units available'] / summary_df['Weighted_Eligibility_Count_80%']) * 100

    if display_race_stats:
        summary_df = add_race_stats(summary_df, hud_hcv_df)

    # Save the summary dataframe
    state_name, year = extract_state_code_and_year(ipums_eligibility_df)
    if display_race_stats:
        file_name = f"{state_name}_{year}_HCV_Gap_Summary_Table_with_race_stats.csv"
    else:
        file_name = f"{state_name}_{year}_HCV_Gap_Summary_Table.csv"

    file_path = os.path.join(output_dir, file_name)
    try:
        summary_df.to_csv(file_path, index=False)
        print(f"HCV Gap Summary dataframe saved successfully to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

    # Save the eligibility dataframe
    save_eligibility_dataframe(ipums_eligibility_df, output_dir)

    print(f"Finished processing {state_name}, {year}")
    return summary_df

