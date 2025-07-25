import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import logging
import os

def create_multi_state_allocation_map(summary_data_dict, output_path=None, show_plot=True):
    """
    Create a choropleth map showing HUD program allocation rates for multiple states.
    
    Parameters:
        summary_data_dict (dict): Dict with state codes as keys and summary DataFrames as values
                                 Example: {'FL': fl_summary_df, 'GA': ga_summary_df}
        output_path (str, optional): Path to save the map (HTML file)
        show_plot (bool): Whether to display the plot
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    
    # Combine all state data
    combined_data = []
    states_list = []
    
    for state, summary_df in summary_data_dict.items():
        if summary_df is None or summary_df.empty:
            logging.warning(f"No data for state: {state}")
            continue
            
        # Check required columns
        required_cols = ['County_Name', 'FIPS_Code', 'summary_of_all_hud_programs_gap_50%']
        if not all(col in summary_df.columns for col in required_cols):
            logging.warning(f"Missing required columns for state: {state}")
            continue
        
        # Add state column and prepare data
        state_df = summary_df.copy()
        state_df['State'] = state
        state_df['FIPS_Code'] = state_df['FIPS_Code'].astype(str).str.zfill(5)
        
        combined_data.append(state_df)
        states_list.append(state)
    
    if not combined_data:
        raise ValueError("No valid data found for any states")
    
    # Combine all states
    plot_df = pd.concat(combined_data, ignore_index=True)
    
    # Create the choropleth map
    fig = px.choropleth(
        plot_df,
        geojson="usa",
        locations='FIPS_Code',
        color='summary_of_all_hud_programs_gap_50%',
        hover_name='County_Name',
        hover_data={
            'State': True,
            'FIPS_Code': False,
            'summary_of_all_hud_programs_gap_50%': ':.1%'
        },
        color_continuous_scale='RdYlBu_r',
        title=f'HUD Program Allocation Rate by County - {", ".join(states_list)} (50% AMI)',
        labels={'summary_of_all_hud_programs_gap_50%': 'Allocation Rate'}
    )
    
    # Update layout for better multi-state view
    fig.update_geos(
        scope="usa",  # Show full USA context
        projection_type="albers usa"
    )
    
    fig.update_layout(
        title_x=0.5,
        font_size=12,
        coloraxis_colorbar=dict(
            title="Allocation Rate",
            tickformat=".1%"
        ),
        height=600
    )
    
    # Save if path provided
    if output_path:
        fig.write_html(output_path)
        logging.info(f"Multi-state map saved to: {output_path}")
    
    # Show if requested
    if show_plot:
        fig.show()
    
    return fig


def create_state_comparison_chart(summary_data_dict, output_path=None, show_plot=True):
    """
    Create a comparison chart showing average allocation rates by state.
    
    Parameters:
        summary_data_dict (dict): Dict with state codes as keys and summary DataFrames as values
        output_path (str, optional): Path to save chart
        show_plot (bool): Whether to display the plot
        
    Returns:
        plotly.graph_objects.Figure: The plotly figure object
    """
    
    state_averages = []
    
    for state, summary_df in summary_data_dict.items():
        if summary_df is None or summary_df.empty:
            continue
            
        if 'summary_of_all_hud_programs_gap_50%' not in summary_df.columns:
            continue
        
        # Calculate state average (weighted by population if weight column exists)
        avg_rate = summary_df['summary_of_all_hud_programs_gap_50%'].mean()
        county_count = len(summary_df.dropna(subset=['summary_of_all_hud_programs_gap_50%']))
        
        state_averages.append({
            'State': state,
            'Average_Allocation_Rate': avg_rate,
            'County_Count': county_count
        })
    
    if not state_averages:
        raise ValueError("No valid data for state comparison")
    
    comparison_df = pd.DataFrame(state_averages)
    comparison_df = comparison_df.sort_values('Average_Allocation_Rate')
    
    # Create bar chart
    fig = px.bar(
        comparison_df,
        x='Average_Allocation_Rate',
        y='State',
        orientation='h',
        title='Average HUD Program Allocation Rate by State',
        labels={
            'Average_Allocation_Rate': 'Average Allocation Rate',
            'State': 'State'
        },
        color='Average_Allocation_Rate',
        color_continuous_scale='RdYlBu_r',
        hover_data={'County_Count': True}
    )
    
    fig.update_layout(
        title_x=0.5,
        height=400,
        showlegend=False,
        xaxis_tickformat='.1%'
    )
    
    # Save if path provided
    if output_path:
        fig.write_html(output_path)
        logging.info(f"State comparison chart saved to: {output_path}")
    
    # Show if requested
    if show_plot:
        fig.show()
    
    return fig


def load_state_summary_data(output_base_dir, states, year):
    """
    Load summary data for multiple states from their output directories.
    
    Parameters:
        output_base_dir (str): Base output directory containing state subdirectories
        states (list): List of state abbreviations
        year (int/str): Year to process
        
    Returns:
        dict: Dictionary with state codes as keys and summary DataFrames as values
    """
    summary_data = {}
    
    for state in states:
        try:
            # Look for the summary file
            state_output_dir = os.path.join(output_base_dir, f"{state}_{year}")
            
            if not os.path.exists(state_output_dir):
                logging.warning(f"Output directory not found for {state}: {state_output_dir}")
                continue
            
            # Find the summary file
            summary_file = None
            for file in os.listdir(state_output_dir):
                if "summary_of_all_hud_programs_linked_summary" in file and file.endswith('.csv'):
                    summary_file = os.path.join(state_output_dir, file)
                    break
            
            if summary_file and os.path.exists(summary_file):
                summary_df = pd.read_csv(summary_file)
                summary_data[state] = summary_df
                logging.info(f"Loaded summary data for {state}: {len(summary_df)} counties")
            else:
                logging.warning(f"Summary file not found for {state}")
                
        except Exception as e:
            logging.error(f"Error loading data for {state}: {e}")
    
    return summary_data


def create_multi_state_dashboard(states, year, output_base_dir, visualization_output_dir=None):
    """
    Create a complete multi-state dashboard.
    
    Parameters:
        states (list): List of state abbreviations to include
        year (int/str): Year to process
        output_base_dir (str): Base directory containing individual state outputs
        visualization_output_dir (str, optional): Where to save multi-state visualizations
        
    Returns:
        dict: Dictionary of figure objects
    """
    
    # Load data for all states
    summary_data = load_state_summary_data(output_base_dir, states, year)
    
    if not summary_data:
        logging.error("No summary data found for any states")
        return {}
    
    logging.info(f"Creating multi-state dashboard for: {list(summary_data.keys())}")
    
    # Set up output directory
    if not visualization_output_dir:
        visualization_output_dir = os.path.join(output_base_dir, "multi_state_visualizations")
    os.makedirs(visualization_output_dir, exist_ok=True)
    
    figures = {}
    
    # Create multi-state map
    try:
        map_path = os.path.join(visualization_output_dir, f"multi_state_allocation_map_{year}.html")
        figures['multi_state_map'] = create_multi_state_allocation_map(
            summary_data, output_path=map_path, show_plot=False
        )
        logging.info("Created multi-state allocation map")
    except Exception as e:
        logging.error(f"Failed to create multi-state map: {e}")
    
    # Create state comparison chart
    try:
        comparison_path = os.path.join(visualization_output_dir, f"state_comparison_{year}.html")
        figures['state_comparison'] = create_state_comparison_chart(
            summary_data, output_path=comparison_path, show_plot=False
        )
        logging.info("Created state comparison chart")
    except Exception as e:
        logging.error(f"Failed to create state comparison chart: {e}")
    
    # Also create individual state maps for reference
    for state, summary_df in summary_data.items():
        try:
            individual_map_path = os.path.join(visualization_output_dir, f"{state}_individual_map_{year}.html")
            from .hudlink_visuals import create_allocation_rate_map  # Import from main visuals module
            figures[f'{state}_individual'] = create_allocation_rate_map(
                summary_df, state, output_path=individual_map_path, show_plot=False
            )
        except Exception as e:
            logging.warning(f"Failed to create individual map for {state}: {e}")
    
    logging.info(f"Multi-state dashboard complete. Created {len(figures)} visualizations.")
    logging.info(f"Visualizations saved to: {visualization_output_dir}")
    
    return figures


# Example usage function
def create_multi_state_visualizations_example():
    """
    Example of how to use the multi-state visualization functions.
    """
    
    # Example 1: If you have the data already loaded
    # summary_data = {
    #     'FL': florida_summary_df,
    #     'GA': georgia_summary_df,
    #     'AL': alabama_summary_df
    # }
    # fig = create_multi_state_allocation_map(summary_data)
    
    # Example 2: Load data from output directories and create full dashboard
    states = ['FL', 'GA', 'AL']
    year = 2023
    output_base_dir = './output'
    
    figures = create_multi_state_dashboard(
        states=states,
        year=year,
        output_base_dir=output_base_dir,
        visualization_output_dir='./multi_state_visualizations'
    )
    
    return figures