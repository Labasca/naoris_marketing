import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .utilities import custom_price_format, human_format


def calculate_initial_liquidity(database_data, max_total_supply, starting_price, liquidity_percent_tge):
    df_database = pd.DataFrame(database_data)
    liquidity_row = df_database[df_database['data_input'] == 'Liquidity']

    if not liquidity_row.empty:
        liquidity_percentage = liquidity_row['distribution'].iloc[0] * (liquidity_percent_tge/100)
        x_initial = max_total_supply * liquidity_percentage  # Initial token amount in the pool
        y_initial = x_initial * starting_price  # Initial USD amount in the pool
    else:
        raise ValueError("Liquidity data not found in the database")

    return x_initial, y_initial


def simulate_price_change(processed_emissions_data, x_initial, y_initial, expected_demand, expected_demand_tge):
    df_emissions = pd.DataFrame(processed_emissions_data)
    inflation_data = calculate_inflation(processed_emissions_data)  # This function needs to return the inflation data correctly

    prices_data = []
    y_taken_data = []  # List to accumulate y_taken values for each month

    x = x_initial
    y = y_initial
    k = x_initial * y_initial  # Constant product

    for month in sorted(df_emissions['Months'].unique()):
        # Selling Pressure
        tokens_sold = df_emissions[df_emissions['Months'] == month].select_dtypes(include=['number']).sum(axis=1).iloc[0]
        x += tokens_sold  # Increase token amount by tokens sold
        y_old = y
        y = k / x  # Adjust USD amount to maintain constant product
        y_taken = y_old - y  # Calculate how much Y was taken away

        # Store y_taken for each month
        y_taken_data.append({'Months': month, 'SellingPressure': y_taken})

        # Adjust demand based on the month
        current_demand = expected_demand_tge if month == 0 else expected_demand

        # Calculate inflation multiplier
        inflation_factor = inflation_data.loc[inflation_data['Months'] == month, 'Inflation'].values[0]
        demand_inflation_multiplier = (100 / inflation_factor) / 100

        if month != 0:  # Do not adjust the initial month's expected demand
            current_demand *= demand_inflation_multiplier

        # Buying Pressure
        y += current_demand  # Increase USD amount by adjusted demand
        x_old = x
        x = k / y  # Adjust token amount to maintain constant product

        # Calculate new price before inflation
        price = y / x

        # Adjust the price by the inflation factor
        adjusted_price = price * inflation_factor

        # Logging for each month
        prices_data.append({'Months': month, 'Price': adjusted_price, 'Inflation': inflation_factor, 'Demand': current_demand})

    prices_df = pd.DataFrame(prices_data)
    y_taken_df = pd.DataFrame(y_taken_data)  # Create DataFrame from the list of y_taken values

    return prices_df, y_taken_df  # Return both DataFrames




def calculate_additional_y_needed(processed_emissions_data, x_initial, y_initial):
    df_emissions = pd.DataFrame(processed_emissions_data)
    k = x_initial * y_initial

    # Calculate state after initial sell
    tokens_sold = df_emissions[df_emissions['Months'] == 0].select_dtypes(include=['number']).sum(axis=1).iloc[0]
    x_after_sell = x_initial + tokens_sold
    y_after_sell = k / x_after_sell

    # Calculate additional Y needed to bring Y back to initial
    additional_y_needed = y_initial - y_after_sell

    return additional_y_needed


def plot_monthly_price_changes(price_data):
    if price_data.empty:
        st.error("No price data available to display.")
        return None, None

    # Check if required columns are present
    if not {'Months', 'Price', 'Demand'}.issubset(price_data.columns):
        st.error("Required data columns are missing.")
        return None, None

    # Calculate the average of all Demand values
    average_y = price_data['Demand'].mean()

    # Create the text for hover information
    hover_text = [f"Demand needed for Month {month:.0f}:<br>{human_format(demand)}" for month, demand in
                  zip(price_data['Months'], price_data['Demand'])]

    # Create a grouped bar chart
    fig = go.Figure(data=[
        go.Bar(
            name='Demand',
            x=price_data['Months'],
            y=price_data['Demand'],
            marker_color='#80aaff',
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',  # Custom hover template
            textposition='none'  # Remove data labels

        )
    ])

    # Update the layout
    fig.update_layout(
        xaxis_title='Months',
        yaxis_title='Demand Needed ($)',
        xaxis=dict(showgrid=True),
        barmode='group',
        hovermode='x',
        height=350,
        margin=dict(t=0, b=0, l=0, r=0)
    )

    fig.update_yaxes(type='linear')  # Ensures linear scale on y-axis for clarity

    return fig, average_y


def calculate_supply_shock(processed_emissions_data):
    df = pd.DataFrame(processed_emissions_data)
    df['Total Released This Month'] = df.sum(axis=1)  # Sum up all tokens released in the month across all columns
    df['Cumulative Tokens'] = df['Total Released This Month'].cumsum()  # Cumulative sum of tokens released until the current month
    df['Supply Shock'] = (df['Total Released This Month'] / df['Cumulative Tokens'].shift(1)).fillna(0)  # Calculate the supply shock percentage

    return df[['Months', 'Supply Shock', 'Total Released This Month', 'Cumulative Tokens']]


def plot_supply_shock(processed_emissions_data, selected_month):
    df = calculate_supply_shock(processed_emissions_data)
    df['Supply Shock'] *= 100  # Convert to percentage for display

    max_supply_shock = max(df['Supply Shock'])
    min_supply_shock = df['Supply Shock'].min()

    def get_supply_shock_value(month):
        values = df.loc[df['Months'] == month, 'Supply Shock'].values
        return values[0] if len(values) > 0 else None

    # Retrieve data safely
    selected_supply_shock = get_supply_shock_value(selected_month)
    previous_supply_shock = get_supply_shock_value(selected_month - 1)
    future_supply_shock = get_supply_shock_value(selected_month + 1)

    # Calculate supply shock strength if data is available
    def calculate_shock_strength(shock):
        return ((shock - min_supply_shock) / (max_supply_shock - min_supply_shock) * 100) if shock is not None else None

    selected_supply_shock_strength = calculate_shock_strength(selected_supply_shock)
    previous_supply_shock_strength = calculate_shock_strength(previous_supply_shock)
    future_supply_shock_strength = calculate_shock_strength(future_supply_shock)

    # Create the Plotly bar chart with a custom color scale
    custom_color_scale = ["#6699ff", "#e60000"]  # Gradient from blue to red
    supply_shock_chart = px.bar(df, x='Months', y='Supply Shock',
                                labels={'Supply Shock': 'Supply Shock Percentage'},
                                color='Supply Shock',
                                color_continuous_scale=custom_color_scale,
                                hover_data={'Months': True, 'Supply Shock': ':.2f%'})
    supply_shock_chart.update_traces(
        hovertemplate="<b>Month %{x}</b><br>Supply Shock: %{y:.2f}%"
    )
    supply_shock_chart.update_layout(
        xaxis_title='Months',
        xaxis=dict(showgrid=True),
        yaxis=dict(
            title='Supply Shock (%)',
            showgrid=True,
            tickformat='%',
            tickvals=[i for i in range(0, int(1.2 * max_supply_shock) + 1, int(1.2 * max_supply_shock / 5))],
            ticktext=[f"{i}%" for i in range(0, int(1.2 * max_supply_shock) + 1, int(1.2 * max_supply_shock / 5))],
            range=[0, 1.2 * max_supply_shock]
        ),
        hovermode='x',
        margin=dict(t=0, b=0, l=0, r=0),
        height=400
    )
    supply_shock_chart.update_coloraxes(colorbar=dict(
        title='Supply Shock %',
        tickvals=[i for i in range(0, int(1.2 * max_supply_shock) + 1, int(1.2 * max_supply_shock / 5))],
        ticktext=[f"{i}%" for i in range(0, int(1.2 * max_supply_shock) + 1, int(1.2 * max_supply_shock / 5))]
    ))

    # Adding an annotation for the selected month
    if selected_month in df['Months'].values:
        supply_shock_chart.add_annotation(
            x=selected_month,
            y=selected_supply_shock,
            text="Current Month",
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40,
            bgcolor='rgba(60, 60, 60, 0.85)',  # Semi-transparent background
            borderpad=4  # Padding around the text
        )

    return supply_shock_chart, selected_supply_shock_strength, previous_supply_shock_strength, future_supply_shock_strength, selected_supply_shock, previous_supply_shock, future_supply_shock


def calculate_inflation(processed_emissions_data):
    df = pd.DataFrame(processed_emissions_data)
    df['Total Released This Month'] = df.sum(axis=1)  # Sum up all tokens released in the month across all columns
    df['Cumulative Tokens'] = df[
        'Total Released This Month'].cumsum()  # Cumulative sum of tokens released until the current month

    # Calculate inflation based on the first month's release
    month_0_release = df['Total Released This Month'].iloc[0] if len(
        df) > 0 else 1  # Default to 1 to avoid division by zero
    df['Inflation'] = (100/(df['Cumulative Tokens'] / month_0_release))/100


    return df[['Months', 'Inflation', 'Total Released This Month', 'Cumulative Tokens']]



def create_price_chart(processed_emissions_data, x_initial, y_initial, expected_demand, expected_demand_tge):
    price_data, y_taken = simulate_price_change(processed_emissions_data, x_initial, y_initial, expected_demand, expected_demand_tge)

    # Filter data for the first 24 months
    price_data_first_24 = price_data[price_data['Months'] <= 48]

    # Apply custom formatting for hover and y-axis labels
    price_data_first_24['Formatted Price'] = price_data_first_24['Price'].apply(custom_price_format)

    # Generate custom hover text for each data point
    hover_texts = []
    for index, row in price_data_first_24.iterrows():
        # Convert month to integer and use "TGE" for month 0, otherwise use "Month X"
        month_label = "TGE" if row['Months'] == 0 else f"Month {int(row['Months'])}"  # Convert to int here
        hover_texts.append(f"{month_label}<br>Price: <b>{row['Formatted Price']}</b>")

    # Create the line plot with markers and custom formatted hover data
    fig = px.line(price_data_first_24, x='Months', y='Price', markers=True)

    # Set the custom hover text for each data point
    fig.update_traces(
        hovertemplate='%{text}<extra></extra>',
        text=hover_texts
    )

    # Determine positions for 5 evenly spaced gridlines
    min_price, max_price = price_data_first_24['Price'].min(), price_data_first_24['Price'].max()
    tick_values = np.linspace(min_price, max_price, 5)

    # Update layout for gridlines and Y-axis tick text
    fig.update_layout(
        xaxis_title='Months',
        yaxis_title='Price ($)',
        xaxis=dict(showgrid=True, range=[0, 48]),  # Set the range for the x-axis
        yaxis=dict(
            showgrid=True,
            range=[min_price, max_price],  # Set the range for the y-axis
            tickvals=tick_values,
            ticktext=[custom_price_format(val) for val in tick_values]
        ),
        hovermode='x',
        hoverlabel=dict(namelength=1),
        height=350,
        margin=dict(t=0, b=0, l=0, r=0)
    ).update_traces(marker=dict(size=5))

    return fig



def create_price_and_supply_shock_chart(processed_emissions_data, x_initial, y_initial, expected_demand, expected_demand_tge, bar_color='#434343'):
    price_data, y_taken = simulate_price_change(processed_emissions_data, x_initial, y_initial, expected_demand, expected_demand_tge)
    supply_shock_data = calculate_supply_shock(processed_emissions_data)

    # Calculate average monthly price
    monthly_price_average = price_data['Price'].mean()

    # Apply custom formatting to the price data
    price_data['Formatted Price'] = price_data['Price'].apply(custom_price_format)
    merged_data = price_data.merge(supply_shock_data, on='Months')

    marker_sizes = [10 if month % 4 == 0 else 0 for month in merged_data['Months']]

    # Initialize the figure
    fig = go.Figure()

    # Add bar plot for supply shocks on the primary y-axis, formatted as percentage
    fig.add_trace(go.Bar(
        x=merged_data['Months'],
        y=merged_data['Supply Shock'] * 100,  # Convert shock value to percentage
        name='Supply Shock',
        marker=dict(color=bar_color),
        hoverinfo='none',  # This ensures no text is displayed on the bar itself, but hover still enabled
        hovertemplate='%{y:.1f}%'  # Format hover text with one decimal place as a percentage
    ))

    fig.add_trace(go.Scatter(
        x=merged_data['Months'],
        y=merged_data['Formatted Price'],
        mode='lines+markers+text',  # Include lines, markers, and text
        name='Price',
        yaxis='y2',
        line=dict(color='#80aaff', width=4),
        marker=dict(size=marker_sizes, opacity=1),  # Custom marker sizes and opacities
        text=[f'{price}' if month % 4 == 0 else '' for month, price in
              zip(merged_data['Months'], merged_data['Formatted Price'])],  # Show labels only every 4 months
        textposition="top center",  # Position text above the markers
        textfont=dict(
            size=14,  # Specify text size here
            color="white"  # Specify text color here
        ),
        hovertemplate='Month: %{x}<br>Price: %{y}<extra></extra>',
    ))

    # Determine the maximum value for the formatted price to set the y2 axis range
    max_price = max(merged_data['Price'])  # Keep this for calculating range, as the formatted price is a string
    max_supply_shock = max(merged_data['Supply Shock']) * 100  # Find max supply shock value and convert to percentage

    # Update layout for two y-axes
    fig.update_layout(
        xaxis_title='Months',
        xaxis=dict(showgrid=True, range=[-1, 49]),  # Set the range for the x-axis
        yaxis=dict(
            title='Supply Shock (%)',
            showgrid=False,
            range=[0, 2 * max_supply_shock],  # Set y max as twice the maximum supply shock observed
            tickvals=[0, 0.5 * max_supply_shock, max_supply_shock, 1.5 * max_supply_shock, 2 * max_supply_shock],
            ticktext=[f'{val:.1f}%' for val in [0, 0.5 * max_supply_shock, max_supply_shock, 1.5 * max_supply_shock, 2 * max_supply_shock]]
        ),
        yaxis2=dict(
            title='Price ($)',
            overlaying='y',
            side='right',
            showgrid=True,
            range=[0, max_price * 1.1],  # Ensure range includes all price data, adjust scale appropriately
            ticktext=[custom_price_format(val) for val in np.linspace(0, max_price * 1.1, 5)],  # Custom formatted ticks
            tickvals=np.linspace(0, max_price * 1.1, 5)
        ),
        hovermode='x unified',
        margin=dict(t=0, b=0, l=0, r=0),
        height=400
    )
    return fig, monthly_price_average












def calculate_monthly_returns(price_data):
    if price_data.empty:
        raise ValueError("Price data is empty in calculate_monthly_returns")
    price_data['Return'] = price_data['Price'].pct_change()
    return price_data

def calculate_monthly_volatility(price_data):
    if price_data.empty:
        raise ValueError("Price data is empty at the start of calculate_monthly_volatility")

    price_data_with_returns = calculate_monthly_returns(price_data)

    if price_data_with_returns.empty:
        raise ValueError("Price data with returns is empty in calculate_monthly_volatility")

    # Calculate mean of monthly changes
    mean_change = price_data_with_returns['Return'].mean()

    # Calculate the deviation for each month and square it
    price_data_with_returns['Deviation'] = ((price_data_with_returns['Return'] / mean_change) ** 2)/100

    # Create a DataFrame for the chart
    volatility_data = price_data_with_returns[['Months', 'Deviation']].copy()
    volatility_data.rename(columns={'Deviation': 'Volatility'}, inplace=True)

    return volatility_data

def create_volatility_chart(price_data):
    monthly_volatility = calculate_monthly_volatility(price_data)

    if monthly_volatility.empty:
        raise ValueError("Monthly volatility data is empty in create_volatility_chart")

    monthly_volatility = monthly_volatility[monthly_volatility['Months'] > 0]

    fig = px.area(monthly_volatility, x='Months', y='Volatility',
                  template='plotly_white')

    # Update hover template to display Month and Volatility
    hover_template = "Month: %{x}<br>Volatility: %{y:.2f}"  # Format volatility with 2 decimal places
    fig.update_traces(hovertemplate=hover_template)

    fig.update_layout(xaxis_title='Months',
                      yaxis_title='Volatility',
                      xaxis=dict(showgrid=True),
                      yaxis=dict(showgrid=True, tickformat=".2f"),  # Format y-axis tick labels
                      hovermode='x',
                      height=350,
                      margin=dict(t=0, b=0, l=0, r=0),
                      showlegend=False)
    return fig