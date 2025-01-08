import pandas as pd
import plotly.graph_objects as go
import numpy as np
from .utilities import human_format1, custom_price_format


def calculate_price_impact(x_initial, y_initial, k, change_amount, action='sold'):
    """
    Calculate the impact on price if a certain number of tokens were sold or bought from the pool.
    :param x_initial: Initial token amount in the pool.
    :param y_initial: Initial USD amount in the pool.
    :param k: Constant product (x_initial * y_initial).
    :param change_amount: Number of tokens sold or bought, or percentage for buying.
    :param action: 'sold' for selling tokens, 'bought' for buying tokens.
    :return: New price after the tokens are sold or bought.
    """
    if action == 'sold':
        x_new = x_initial + change_amount  # Increase token amount by tokens sold
    elif action == 'bought':
        token_change = x_initial * (change_amount / 100)  # Change as a percentage of initial tokens
        x_new = max(x_initial - token_change, 0)  # Decrease token amount by tokens bought, ensuring non-negative
    else:
        raise ValueError("Action must be 'sold' or 'bought'")

    # Ensure x_new is not zero to avoid division by zero
    if x_new == 0:
        raise ValueError("Insufficient liquidity for this transaction")

    y_new = k / x_new  # Adjust USD amount to maintain constant product
    new_price = y_new / x_new  # New price per token
    return new_price



def create_impact_chart(x_initial, y_initial, tge_tokens, tge_price, selling_pressure, steps=6):
    k = x_initial * y_initial  # Constant product
    price_changes = {'Tokens Sold or Bought': [0], 'Price': [tge_price]}



    # Calculate price impact for selling
    for i in range(1, steps + 1):
        tokens_change = tge_tokens * (i / steps)
        price = calculate_price_impact(x_initial, y_initial, k, tokens_change, action='sold')
        price_changes['Tokens Sold or Bought'].append(-tokens_change)  # Negative for sold tokens
        price_changes['Price'].append(price)

    # Determine the percentage sold at lowest point
    min_tokens_sold = min(price_changes['Tokens Sold or Bought'])
    percentage_sold = (abs(min_tokens_sold) / tge_tokens) * 100

    # Reset to TGE price
    price_changes['Tokens Sold or Bought'].append(0)
    price_changes['Price'].append(tge_price)

    # Calculate price impact for buying
    for i in range(1, steps + 1):
        percentage_change = (i / steps) * 50  # Assuming 50% of initial tokens for buying
        tokens_bought = x_initial * (percentage_change / 100)  # Calculate actual tokens bought
        price = calculate_price_impact(x_initial, y_initial, k, percentage_change, action='bought')
        price_changes['Tokens Sold or Bought'].append(tokens_bought)  # Positive for bought tokens
        price_changes['Price'].append(price)

    # Determine the percentage bought at highest point
    max_tokens_bought = max(price_changes['Tokens Sold or Bought'])
    percentage_bought = (max_tokens_bought / x_initial) * 100

    impact_data = pd.DataFrame(price_changes)
    impact_data.sort_values(by='Tokens Sold or Bought', inplace=True)

    # Create 'Hover Text' column
    impact_data['Hover Text'] = impact_data.apply(
        lambda
            row: f"Tokens Sold: {human_format1(abs(row['Tokens Sold or Bought']))}<br>Price: {custom_price_format(row['Price'])}"
        if row['Tokens Sold or Bought'] < 0 else
        f"Tokens Bought: {human_format1(row['Tokens Sold or Bought'])}<br>Price: {custom_price_format(row['Price'])}",
        axis=1)

    fig = go.Figure()

    # Use selling_pressure for annotations
    sold_label = f"{selling_pressure:.2f}% Sold"
    bought_label = f"{selling_pressure:.2f}% Bought"

    # Add a vertical line at x=0
    fig.add_vline(x=0, line_width=1, line_dash="solid", line_color="#808080")

    # Re-add the price data line with custom hovertext
    fig.add_trace(go.Scatter(
        x=impact_data['Tokens Sold or Bought'],
        y=impact_data['Price'],
        mode='lines+markers',
        hovertemplate=impact_data['Hover Text'],
        name="",  # Set trace name to empty
        showlegend=False  # Hide the legend entry
    ))

    # Determine the range of y-values and log scale tick values
    min_price, max_price = impact_data['Price'].min(), impact_data['Price'].max()
    log_ticks = np.logspace(np.log10(min_price), np.log10(max_price), num=5)

    # Logarithmize the annotation y-coordinates and add an offset
    offset_factor = 1.2  # Adjust this factor to change the height of the labels
    log_initial_price = np.log10(tge_price * offset_factor)
    log_min_price = np.log10(impact_data['Price'].min() * offset_factor)
    log_max_price = np.log10(impact_data['Price'].max() * offset_factor)

    # Add data labels with adjusted y-coordinates
    fig.add_annotation(x=0, y=log_initial_price, text="Initial Price", showarrow=False)
    fig.add_annotation(x=min_tokens_sold, y=log_min_price, text=f"{selling_pressure}% Sold", showarrow=False)
    fig.add_annotation(x=max_tokens_bought, y=log_max_price, text=f"{selling_pressure}% Bought", showarrow=False)

    # [Rest of your code for updating axes and layout...]

    fig.update_yaxes(tickvals=log_ticks, ticktext=[custom_price_format(tick) for tick in log_ticks])
    fig.update_layout(
        xaxis_title='Tokens Bought or Sold',
        yaxis_title='Price ($)',
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, type='log'),
        height=350,
        margin=dict(t=0, b=0, l=0, r=0)
    )

    return fig

