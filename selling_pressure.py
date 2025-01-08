# selling_pressure.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def process_emissions_data(data, selling_pressure_percentage):
    df = pd.DataFrame(data)

    # Rename the first column to 'Months' for clarity
    df.rename(columns={df.columns[0]: 'Months'}, inplace=True)

    # Ensure 'Months' column is numeric
    df['Months'] = pd.to_numeric(df['Months'], errors='coerce')

    # Convert selling pressure percentage to a decimal
    selling_pressure_factor = selling_pressure_percentage / 100

    # Convert all other columns to numeric and apply selling pressure
    for col in df.columns:
        if col != 'Months':
            df[col] = pd.to_numeric(df[col], errors='coerce') * selling_pressure_factor

    # Sum up emissions for each month (non-cumulative)
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

    # Database data processing and investor calculations (assuming this part is correctly implemented)
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

def create_emissions_chart(emissions_data, database_data, selling_pressure_source, selling_pressure):
    df_emissions = pd.DataFrame(emissions_data)
    df_database = pd.DataFrame(database_data)

    # Get a list of pool names based on the selling pressure source
    if selling_pressure_source == "Circulation":
        df_database['circulation'] = df_database['circulation'].apply(lambda x: x == 'TRUE')
        selected_pools = df_database[df_database['circulation']]['data_input'].tolist()
    elif selling_pressure_source == "Investors":
        df_database['is_investor'] = df_database['is_investor'].apply(lambda x: x == 'TRUE')
        selected_pools = df_database[df_database['is_investor']]['data_input'].tolist()
    else:
        selected_pools = df_emissions.columns[1:]  # Exclude 'Months' column

    # Filter emissions data to include only selected pools
    df_emissions = df_emissions[['Month'] + [pool for pool in selected_pools if pool in df_emissions.columns]]

    monthly_sum = process_emissions_data(df_emissions, selling_pressure)

    # Reset index to make 'Months' a column
    monthly_sum = monthly_sum.reset_index()

    return monthly_sum

