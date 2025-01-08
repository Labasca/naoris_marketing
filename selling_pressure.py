# selling_pressure.py

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from .utilities import human_format, make_unicode_bold, round_to_nearest, human_format1


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

    fig = px.bar(monthly_sum, x='Months', y=monthly_sum.columns[1:],  # Exclude 'Months' column for y-axis
                 title="Total Token Emissions by Month")
    fig.update_layout(xaxis_title='Months', yaxis_title='Total Emissions')

    if 'Months' in monthly_sum.columns:
        month_0_emissions = monthly_sum[monthly_sum['Months'] == 0]
        tokens_sold_month_0 = month_0_emissions.iloc[0, 1:].sum()  # Sum up all tokens for month 0
    else:
        tokens_sold_month_0 = 0

    return monthly_sum, fig, tokens_sold_month_0




def process_and_display_emissions_with_price(data, database_data, selling_pressure_source, selling_pressure_percentage, starting_price):
    df_emissions = pd.DataFrame(data)
    df_database = pd.DataFrame(database_data)
    df_database1 = pd.DataFrame(database_data)

    # Identify circulation pools
    df_database1['circulation'] = df_database1['circulation'].apply(lambda x: x == 'TRUE')
    circulation_pools = df_database1[df_database1['circulation']]['data_input'].tolist()

    # All pools are considered for unlocks
    unlocks_pools = df_emissions.columns[1:]  # Exclude 'Month' column

    # Filter emissions data to include only circulation pools for the calculation of month_0_mcap
    df_emissions_circulation = df_emissions[
        ['Month'] + [pool for pool in circulation_pools if pool in df_emissions.columns]]

    # Calculate month 0 market cap (mcap) based on circulation pools
    month_0_data = df_emissions_circulation[df_emissions_circulation['Month'] == 0]
    month_0_mcap = month_0_data[circulation_pools].astype(float).fillna(0).sum(axis=1).iloc[0] * starting_price

    # Calculate month 0 market cap based on unlocks pools (all pools)
    month_0_data_unlocks = df_emissions[df_emissions['Month'] == 0]
    month_0_mcap_unlocks = month_0_data_unlocks[unlocks_pools].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1).iloc[0] * starting_price


    # Get a list of pool names based on the selling pressure source
    if selling_pressure_source == "Circulation":
        df_database['circulation'] = df_database['circulation'].apply(lambda x: x == 'TRUE')
        selected_pools = df_database[df_database['circulation']]['data_input'].tolist()
    elif selling_pressure_source == "Investors":
        df_database['is_investor'] = df_database['is_investor'].apply(lambda x: x == 'TRUE')
        selected_pools = df_database[df_database['is_investor']]['data_input'].tolist()
    else:
        selected_pools = df_emissions.columns[1:]  # Exclude 'Month' column

    # Filter emissions data to include only selected pools
    df_emissions = df_emissions[['Month'] + [pool for pool in selected_pools if pool in df_emissions.columns]]

    # Convert selling pressure percentage to a decimal
    selling_pressure_factor = selling_pressure_percentage / 100

    # Convert all other columns to numeric, apply selling pressure, and multiply by starting price
    for col in df_emissions.columns:
        if col != 'Month':
            df_emissions[col] = pd.to_numeric(df_emissions[col],
                                              errors='coerce') * selling_pressure_factor * starting_price

    # Sum up emissions for each month (non-cumulative) and then sum across all selected pools
    monthly_sum = df_emissions.groupby(['Month']).sum()
    monthly_sum['Total Emissions'] = monthly_sum.sum(axis=1)

    # Reset index to make 'Month' a column again
    monthly_sum = monthly_sum.reset_index()

    # Convert 'Month' column to integers if they are not already
    monthly_sum['Month'] = monthly_sum['Month'].astype(int)

    # Determine the maximum y-value, rounded to the nearest 100000
    y_max_rounded = round_to_nearest(monthly_sum['Total Emissions'].max(), 100000)

    # Determine tick values for y-axis
    tick_values = np.linspace(0, y_max_rounded, num=5)  # Example with 5 ticks

    # Create the plot
    fig = px.bar(monthly_sum, x='Month', y='Total Emissions')

    # Add a column for formatted Total Emissions
    monthly_sum['Formatted Emissions'] = monthly_sum['Total Emissions'].apply(human_format1)

    # Update layout and format y-axis
    fig.update_layout(xaxis_title='Months',
                      yaxis_title='Buying Pressure ($)',
                      xaxis=dict(showgrid=True),
                      yaxis=dict(showgrid=True, tickvals=tick_values),
                      hovermode='x',
                      height=450,
                      margin=dict(t=0, b=0, l=0, r=0)
                      )

    # Use a custom function to format y-axis labels
    fig.update_yaxes(ticktext=[human_format1(val) for val in tick_values])

    # Hide data label text on the bars
    fig.update_traces(texttemplate='')

    # Conditional hovertemplate for each bar
    hovertexts = [
        'TGE<br>Needed Demand: ' + val if month == 0 else 'Month ' + str(month) + '<br>Needed Demand: ' + val
        for month, val in zip(monthly_sum['Month'], monthly_sum['Formatted Emissions'])]
    fig.update_traces(hovertemplate=hovertexts)

    month_0_demand = monthly_sum[monthly_sum['Month'] == 0]['Total Emissions'].iloc[0]

    # Return the processed data and the figure
    return monthly_sum, fig, month_0_demand, month_0_mcap, month_0_mcap_unlocks


def create_combined_chart(tge_price, emissions_data, price_data, database_data, selling_pressure_source, y_taken):
    if not isinstance(y_taken,
                      pd.DataFrame) or 'Months' not in y_taken.columns or 'SellingPressure' not in y_taken.columns:
        raise ValueError("y_taken must be a DataFrame with 'Months' and 'SellingPressure' columns.")

    # Function to determine the color and categorize based on the pool type
    def categorize_pool(pool_name):
        if pool_name in investors_pools:
            return 'red', 'investor'  # Color and category for investors
        elif pool_name in circulation_pools:
            return '#d9d9d9', 'circulation'  # Color and category for circulation
        else:
            return '#737373', 'unlocks'  # Color and category for unlocks (default)

    # Prepare pool lists based on the database data
    df_database = pd.DataFrame(database_data)
    df_database['circulation'] = df_database['circulation'].apply(lambda x: x == 'TRUE')
    df_database['is_investor'] = df_database['is_investor'].apply(lambda x: x == 'TRUE')
    circulation_pools = df_database[df_database['circulation']]['data_input'].tolist()
    investors_pools = df_database[df_database['is_investor']]['data_input'].tolist()

    # Merge the provided 'y_taken' data (assuming it includes a 'Months' column for indexing)
    combined_data = pd.merge(emissions_data[['Months']], y_taken, on='Months', how='left')

    # Invert the SellingPressure values to be negative
    combined_data['SellingPressure'] = -combined_data['SellingPressure'].abs()

    # Prepare a DataFrame for hover text
    agg_data = {'Months': combined_data['Months'].tolist(), 'TotalValue': combined_data['SellingPressure'].tolist(),
                'HoverText': []}
    for index, row in combined_data.iterrows():
        hover_text = {'investor': [], 'circulation': [], 'unlocks': []}
        month = row['Months']
        for col in emissions_data.columns:
            if col != 'Months':
                value = -1 * emissions_data.loc[emissions_data['Months'] == month, col].sum()
                if value != 0:
                    formatted_value = human_format(value)
                    color, category = categorize_pool(col)
                    hover_text[category].append(f"<span style='color:{color};'>{col}: {formatted_value}</span>")

        # Concatenate hover text in the order of investor, circulation, unlocks
        ordered_hover_text = hover_text['investor'] + hover_text['circulation'] + hover_text['unlocks']

        # Prepend header with month information
        if month == 0:
            month_header = "Selling Pressure at TGE:<br>"
        else:
            month_header = f"Selling Pressure for Month {month}:<br>"
        ordered_hover_text.insert(0, month_header)

        # Append total combined selling pressure
        formatted_total_value = human_format(row['SellingPressure'])
        total_bold = make_unicode_bold("Total:")
        ordered_hover_text.append(f"<br>{total_bold} {formatted_total_value}")

        agg_data['HoverText'].append('<br>'.join(ordered_hover_text))

    agg_df = pd.DataFrame(agg_data)

    # Calculate average selling pressure
    average_selling_pressure = agg_df['TotalValue'].mean()

    month_0_value = agg_df[agg_df['Months'] == 0]['TotalValue'].iloc[0]

    # Creating the plot
    fig = go.Figure(go.Bar(
        x=agg_df['Months'],
        y=agg_df['TotalValue'],
        hovertext=agg_df['HoverText'],
        hoverinfo='text',
        marker_color='#FF3333'  # Red color
    ))

    # Determine Y-axis range and calculate custom tick labels
    y_min, y_max = agg_df['TotalValue'].min(), agg_df['TotalValue'].max()
    y_range = y_max - y_min
    num_ticks = 5  # You can adjust the number of ticks here
    y_tick_interval = round_to_nearest(y_range / (num_ticks - 1), 10000)  # Adjust rounding as needed
    y_ticks = [round_to_nearest(y_min + i * y_tick_interval, 10000) for i in range(num_ticks)]
    y_tick_labels = [human_format(tick) for tick in y_ticks]

    # Update chart layout with vertical gridlines and custom y-axis labels
    fig.update_layout(
        xaxis_title="Months",
        yaxis_title="Selling Pressure ($)",
        xaxis=dict(
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,
            tickvals=y_ticks,
            ticktext=y_tick_labels
        ),
        hovermode='x',
        height=350,
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig, month_0_value, average_selling_pressure



