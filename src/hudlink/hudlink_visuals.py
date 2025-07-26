"""
hudlink_visuals.py

Visualization module for hudlink housing analysis package.
Creates interactive choropleth maps showing HUD program allocation rates.

Functions:
    maybe_create_gap_visual(config): Main entry point for visualization creation
    create_gap_visual(config): Core visualization logic
    load_state_gap_data(output_dir, state, target_program): Load state summary data
    create_choropleth_map(combined_df, states, target_program, output_path): Create the map
"""

# Fix numpy 2.0 compatibility issue
import numpy as np
if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_

import pandas as pd
import logging
import os
import glob
import json
import webbrowser

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    px = None


def maybe_create_gap_visual(config):
    """
    Create gap visual if enabled in config and plotly is available.
    
    This is the main entry point called from state_processor.py.
    
    Parameters:
        config (dict): Configuration dictionary
    """
    create_gap_viz = config.get("create_gap_visual", False)
    
    if not create_gap_viz:
        logging.info("Gap visual creation disabled in config")
        return
    
    if not PLOTLY_AVAILABLE:
        logging.warning("Plotly not installed - skipping gap visual creation")
        logging.info("To enable visualizations: pip install plotly")
        return
    
    logging.info("Creating gap visual...")
    try:
        fig = create_gap_visual(config)
        if fig:
            logging.info("Gap visual creation completed successfully")
        else:
            logging.warning("Gap visual creation failed")
    except Exception as e:
        logging.error(f"Error creating gap visual: {e}")


def create_gap_visual(config):
    """
    Create a single choropleth map showing HUD program allocation rates for all states in config.
    
    This function:
    1. Finds the most recent year's data for each state
    2. Uses "Summary of All HUD Programs" or the first program in the list
    3. Creates one map showing allocation rates at 50% AMI for all states
    4. Saves the map to the output directory
    
    Parameters:
        config (dict): Configuration dictionary containing:
                      - states: List of state abbreviations
                      - program_labels: List of HUD program labels  
                      - output_directory: Base output directory
                      - ipums_years: List of years (uses most recent)
    
    Returns:
        plotly.graph_objects.Figure or None: The plotly figure object
    """
    states = config.get("states", [])
    program_labels = config.get("program_labels", [])
    output_dir = config.get("output_directory", "./output")
    years = config.get("ipums_years", [])
    most_recent_year = max(years) if years else "unknown"
    
    if not states:
        logging.warning("No states specified in config - skipping gap visual")
        return None
    
    if not program_labels:
        logging.warning("No program labels specified in config - skipping gap visual")
        return None
    
    # Determine which program to use
    target_program = "Summary of All HUD Programs"
    if target_program not in program_labels:
        target_program = program_labels[0]
        logging.info(f"'Summary of All HUD Programs' not found, using: {target_program}")
    
    logging.info(f"Creating gap visual for {len(states)} states using program: {target_program}")
    
    # Collect data from all states
    all_state_data = []
    
    for state in states:
        try:
            state_data = load_state_gap_data(output_dir, state, target_program, most_recent_year)
            if state_data is not None:
                state_data['State'] = state.upper()
                all_state_data.append(state_data)
                logging.info(f"Loaded data for {state}: {len(state_data)} counties")
            else:
                logging.warning(f"No data found for state: {state}")
                
        except Exception as e:
            logging.error(f"Error loading data for {state}: {e}")
    
    if not all_state_data:
        logging.error("No data found for any states - cannot create gap visual")
        return None
    
    # Combine all state data
    combined_df = pd.concat(all_state_data, ignore_index=True)
    logging.info(f"Combined data: {len(combined_df)} total counties across {len(all_state_data)} states")
    
    # Create the map
    try:
        output_path = os.path.join(output_dir, f"hud_allocation_gap_map_{most_recent_year}.html")
        fig = create_choropleth_map(combined_df, [s.upper() for s in states], target_program, output_path, config)
        
        logging.info(f"Gap visual created successfully: {output_path}")
        return fig
        
    except Exception as e:
        logging.error(f"Failed to create gap visual: {e}")
        return None


def load_state_gap_data(output_dir, state, target_program, year):
    """
    Load the summary data for a state and target program.
    
    Parameters:
        output_dir (str): Base output directory
        state (str): State abbreviation
        target_program (str): Target HUD program name
        year (str/int): Year to look for
        
    Returns:
        pd.DataFrame or None: DataFrame with gap data, or None if not found
    """
    # Look for state directory in the expected format: STATE_YEAR
    state_dir = os.path.join(output_dir, state.upper(), f"{state.upper()}_{year}")
    
    if not os.path.exists(state_dir):
        logging.warning(f"Directory not found: {state_dir}")
        return None
    
    # Look for the target program summary file with flexible pattern matching
    summary_pattern = "*linked_summary*.csv"
    summary_files = glob.glob(os.path.join(state_dir, summary_pattern))
    
    if not summary_files:
        logging.warning(f"No summary files found in {state_dir}")
        return None
    
    # Filter for the target program or use the first available
    target_file = None
    program_key = target_program.replace(' ', '_').lower()
    
    for file_path in summary_files:
        filename = os.path.basename(file_path).lower()
        if program_key in filename:
            target_file = file_path
            break
    
    if not target_file:
        target_file = summary_files[0]  # Use first available file
        logging.info(f"Using first available summary file: {os.path.basename(target_file)}")
    
    # Load the data
    try:
        df = pd.read_csv(target_file)
        
        # Check for required columns
        required_cols = ['County_Name', 'FIPS_Code']
        
        # Find the allocation rate column (updated based on debugging)
        allocation_col = None
        possible_cols = [
            'summary_of_all_hud_programs_allocation_rate_50%',
            'allocation_rate_50%',
            'gap_50%'
        ]
        
        for col in possible_cols:
            if col in df.columns:
                allocation_col = col
                break
        
        if not allocation_col:
            # Try to find any column with 'allocation' and '50%'
            potential_cols = [col for col in df.columns if 'allocation' in col.lower() and '50%' in col]
            if potential_cols:
                allocation_col = potential_cols[0]
                logging.info(f"Using allocation column: {allocation_col}")
            else:
                logging.warning(f"No allocation rate column found in {target_file}")
                logging.info(f"Available columns: {list(df.columns)}")
                return None
        
        if not all(col in df.columns for col in required_cols):
            logging.warning(f"Missing required columns in {target_file}")
            return None
        
        # Clean and prepare the data
        df = df[required_cols + [allocation_col]].copy()
        
        # Handle missing FIPS codes
        df['FIPS_Code'] = pd.to_numeric(df['FIPS_Code'], errors='coerce')
        df = df.dropna(subset=['FIPS_Code', allocation_col])
        
        # Format FIPS codes properly
        df['FIPS_Code'] = df['FIPS_Code'].astype(int).astype(str).str.zfill(5)
        
        # Rename the allocation column to standard name and convert to decimal if needed
        df = df.rename(columns={allocation_col: 'allocation_rate'})
        
        # Convert percentage to decimal if values are > 1 (assuming they're stored as percentages)
        if df['allocation_rate'].max() > 1:
            df['allocation_rate'] = df['allocation_rate'] / 100.0
        
        # Apply Connecticut FIPS code fix if needed
        if state.upper() == 'CT':
            df = fix_ct_fips_codes(df)
        
        logging.info(f"Loaded {len(df)} counties for {state}")
        return df
        
    except Exception as e:
        logging.error(f"Error reading {target_file}: {e}")
        return None


def fix_ct_fips_codes(df):
    """
    Map Connecticut Planning Regions back to old county FIPS codes for visualization.
    
    Connecticut switched to Planning Regions in 2023, but plotly still uses old county boundaries.
    """
    ct_region_to_old_fips = {
        '09110': '09003',  # Capitol Region → Hartford County
        '09120': '09001',  # Greater Bridgeport → Fairfield County  
        '09130': '09007',  # Lower Connecticut River Valley → Middlesex County
        '09140': '09009',  # Naugatuck Valley → New Haven County
        '09150': '09015',  # Northeastern Connecticut → Windham County
        '09160': '09005',  # Northwestern Hills → Litchfield County
        '09170': '09009',  # South Central Connecticut → New Haven County
        '09180': '09011',  # Southeastern Connecticut → New London County
        '09190': '09001',  # Western Connecticut → Fairfield County
    }
    
    # Apply mapping for CT records
    df['FIPS_Code'] = df['FIPS_Code'].map(ct_region_to_old_fips).fillna(df['FIPS_Code'])
    
    return df


def create_choropleth_map(combined_df, states, target_program, output_path, config):
    """
    Create the actual choropleth map using local geojson data.
    
    Parameters:
        combined_df (pd.DataFrame): Combined data from all states
        states (list): List of state abbreviations
        target_program (str): Name of the HUD program being visualized
        output_path (str): Where to save the HTML file
        config (dict): Configuration dictionary
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    
    # Load the bundled US counties geojson data
    geojson_path = os.path.join(os.path.dirname(__file__), 'data', 'us_counties_fips.json')
    
    try:
        with open(geojson_path, 'r') as f:
            counties_geojson = json.load(f)
    except FileNotFoundError:
        logging.warning(f"Geojson file not found at {geojson_path}, using online version")
        counties_geojson = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    except Exception as e:
        logging.error(f"Error loading geojson file: {e}, using online version")
        counties_geojson = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    
    # Create the choropleth map
    fig = px.choropleth(
        combined_df,
        geojson=counties_geojson,
        locations='FIPS_Code',
        color='allocation_rate',
        hover_name='County_Name',
        hover_data={
            'State': True,
            'FIPS_Code': False,
            'allocation_rate': ':.1%'
        },
        color_continuous_scale='viridis',
        title=f'HUD Program Allocation Rate by County - {", ".join(states)}<br>{target_program} (50% AMI)',
        labels={'allocation_rate': 'Allocation Rate'}
    )
    
    # Update map settings
    fig.update_geos(
        scope="usa",
        projection_type="albers usa",
        showlakes=True,
        lakecolor="LightBlue"
    )
    
    # Update layout
    fig.update_layout(
        title_x=0.5,
        title_font_size=16,
        font_size=12,
        coloraxis_colorbar=dict(
            title="Allocation Rate",
            tickformat=".1%",
            title_font_size=14
        ),
        height=600,
        width=1000
    )
    
    # Save the map
    fig.write_html(output_path)
    logging.info(f"Gap visual saved to: {output_path}")
    
    # Open in browser if requested
    if config.get("open_visualizations", False):
        try:
            webbrowser.open(f"file://{os.path.abspath(output_path)}")
            logging.info("Opened visualization in default browser")
        except Exception as e:
            logging.warning(f"Could not open browser: {e}")
    
    return fig