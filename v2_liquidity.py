import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go




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

