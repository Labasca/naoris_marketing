import plotly.express as px
import pandas as pd

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

    return supply_shock_chart, selected_supply_shock, previous_supply_shock, future_supply_shock

def calculate_supply_shock(processed_emissions_data):
    df = pd.DataFrame(processed_emissions_data)
    df['Total Released This Month'] = df.sum(axis=1)  
    df['Cumulative Tokens'] = df['Total Released This Month'].cumsum()
    df['Supply Shock'] = (df['Total Released This Month'] / df['Cumulative Tokens'].shift(1)).fillna(0)
    return df[['Months', 'Supply Shock', 'Total Released This Month', 'Cumulative Tokens']]

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

