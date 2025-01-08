import streamlit as st
import json
import os
import pandas as pd

# Function to load data from a JSON file
def load_data_from_file(filename):
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    filepath = os.path.join(script_dir, 'data', filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

@st.cache_data
def get_sheet_data(sheet_names):
    filenames = {
        'Database': 'Database.json',
        'streamlit_emissions': 'streamlit_emissions.json'
    }
    data = {}
    for name in sheet_names:
        filename = filenames.get(name)
        if filename:
            data[name] = load_data_from_file(filename)
    return data

def process_emissions_data(data, selling_pressure_percentage):
    df = pd.DataFrame(data)
    df.rename(columns={df.columns[0]: 'Months'}, inplace=True)
    df['Months'] = pd.to_numeric(df['Months'], errors='coerce')
    
    selling_pressure_factor = selling_pressure_percentage / 100
    
    for col in df.columns:
        if col != 'Months':
            df[col] = pd.to_numeric(df[col], errors='coerce') * selling_pressure_factor
    
    monthly_sum = df.groupby('Months').sum()
    return monthly_sum

def sum_monthly_emissions(data, selling_pressure_percentage, selected_month, database_data):
    # Convert input data to DataFrame and handle columns
    df = pd.DataFrame(data)
    df.rename(columns={df.columns[0]: 'Months'}, inplace=True)
    df['Months'] = pd.to_numeric(df['Months'], errors='coerce')

    # Apply selling pressure percentage to data
    selling_pressure_factor = selling_pressure_percentage / 100
    df_100SP = df.copy()  # Clone the DataFrame for 100% selling pressure case
    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors='coerce') * selling_pressure_factor
        df_100SP[col] = pd.to_numeric(df_100SP[col], errors='coerce')  # Apply 100% pressure

    # Sum emissions for each month
    df['Emissions_summed'] = df.drop('Months', axis=1).sum(axis=1)
    monthly_emissions_sum = df.groupby('Months')['Emissions_summed'].sum().reset_index()
    monthly_emissions_sum.columns = ['Month', 'Emissions_summed']

    # Sum emissions for 100% selling pressure
    df_100SP['Emissions_summed'] = df_100SP.drop('Months', axis=1).sum(axis=1)
    monthly_emissions_sum_100SP = df_100SP.groupby('Months')['Emissions_summed'].sum().reset_index()
    monthly_emissions_sum_100SP.columns = ['Month', 'Emissions_summed']

    # Safe extraction function
    def safe_extract_emission(month, data_frame):
        if month in data_frame['Month'].values:
            return data_frame.loc[data_frame['Month'] == month, 'Emissions_summed'].values[0]
        else:
            return 0

    # Extract emissions sums safely for both scenarios
    selected_month_emissions_sum = safe_extract_emission(selected_month, monthly_emissions_sum)
    previous_month_emissions_sum = safe_extract_emission(selected_month - 1, monthly_emissions_sum)
    future_month_emissions_sum = safe_extract_emission(selected_month + 1, monthly_emissions_sum)

    # Extract for 100% selling pressure
    selected_month_emissions_sum_100SP = safe_extract_emission(selected_month, monthly_emissions_sum_100SP)
    previous_month_emissions_sum_100SP = safe_extract_emission(selected_month - 1, monthly_emissions_sum_100SP)
    future_month_emissions_sum_100SP = safe_extract_emission(selected_month + 1, monthly_emissions_sum_100SP)

    # Database data processing and investor calculations
    df_investor = pd.DataFrame(database_data)
    df_investor.rename(columns={df_investor.columns[0]: 'data_input', df_investor.columns[8]: 'is_investor'}, inplace=True)
    investor_pools = df_investor[df_investor['is_investor'] == 'TRUE']['data_input'].tolist()

    # Calculate the token unlock for investor pools
    df['Investor_emissions'] = df[investor_pools].sum(axis=1)
    investor_emissions_sums = df.groupby('Months')['Investor_emissions'].sum().reset_index()

    # Safe extraction for investor sums
    def safe_extract_investor(month):
        if month in investor_emissions_sums['Months'].values:
            return investor_emissions_sums.loc[investor_emissions_sums['Months'] == month, 'Investor_emissions'].values[0]
        else:
            return 0

    # Investor emissions sums
    selected_month_investor_sum = safe_extract_investor(selected_month)
    previous_month_investor_sum = safe_extract_investor(selected_month - 1)
    future_month_investor_sum = safe_extract_investor(selected_month + 1)

    # Calculate percentages safely
    def safe_percentage(numerator, denominator):
        return (numerator / denominator) * 100 if denominator != 0 else 0

    selected_month_investor_percent = safe_percentage(selected_month_investor_sum, selected_month_emissions_sum)
    previous_month_investor_percent = safe_percentage(previous_month_investor_sum, previous_month_emissions_sum)
    future_month_investor_percent = safe_percentage(future_month_investor_sum, future_month_emissions_sum)

    return (
        selected_month_emissions_sum,
        previous_month_emissions_sum,
        future_month_emissions_sum,
        selected_month_investor_percent,
        previous_month_investor_percent,
        future_month_investor_percent,
        selected_month_emissions_sum_100SP,
        previous_month_emissions_sum_100SP,
        future_month_emissions_sum_100SP
    )