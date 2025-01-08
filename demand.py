import pandas as pd
import numpy as np


def calculate_required_price_for_mcap(selected_month, real_mcap, data_emissions, database_data, x_initial, y_initial,
                                      selling_pressure_percentage):
    df_emissions = pd.DataFrame(data_emissions)
    df_database = pd.DataFrame(database_data)

    # Identify pools marked as circulation (TRUE in column J)
    circulation_pools = df_database[df_database.iloc[:, 9] == "TRUE"]['data_input'].tolist()

    # Ensure all data in emissions is numeric and fill NaN values with 0
    for col in df_emissions.columns[1:]:
        df_emissions[col] = pd.to_numeric(df_emissions[col], errors='coerce')
    df_emissions.fillna(0, inplace=True)

    # Filter emissions DataFrame to include only matching circulation pool columns
    matching_circulation_pools = [col for col in df_emissions.columns[1:] if col in circulation_pools]

    df_emissions_circulation = df_emissions[['Month'] + matching_circulation_pools]

    # Calculate the total emissions until the selected month (circulating supply)
    total_emissions_until_selected_month = df_emissions_circulation[
        df_emissions_circulation['Month'] <= selected_month].sum(axis=0).sum()

    # Calculate required price based on market cap and circulating supply
    required_price = real_mcap / total_emissions_until_selected_month

    # Calculate k, the constant product
    k = x_initial * y_initial

    # Solve for new_x and new_y
    new_x = (k / required_price) ** 0.5
    new_y = k / new_x

    k_new = new_y * new_x

    return required_price, new_x, new_y


def calculate_required_monthly_demand_to_reach_y_new(selected_month, y_new, data_emissions, database_data, x_initial, y_initial, selling_pressure_percentage, tolerance=1000, max_iterations=50):
    df_emissions = pd.DataFrame(data_emissions)
    df_database = pd.DataFrame(database_data)

    # Filter the pools marked as circulation
    circulation_pools = df_database[df_database.iloc[:, 9] == "TRUE"]['data_input'].tolist()

    # Ensure all emission data is numeric and fill NaN values with 0
    for col in df_emissions.columns[1:]:
        df_emissions[col] = pd.to_numeric(df_emissions[col], errors='coerce')
    df_emissions.fillna(0, inplace=True)

    # Filter emissions DataFrame for circulation pools
    df_emissions = df_emissions[['Month'] + [col for col in circulation_pools if col in df_emissions.columns]]

    k = x_initial * y_initial
    initial_expected_demand = 0
    iteration = 0
    closest_demand = None
    closest_y_diff = float('inf')

    while iteration < max_iterations:
        x = x_initial
        y = y_initial
        expected_demand = initial_expected_demand

        for month in range(1, selected_month + 1):
            tokens_sold = df_emissions[df_emissions['Month'] == month].select_dtypes(include=['number']).sum(axis=1).iloc[0]
            selling_pressure = tokens_sold * (selling_pressure_percentage / 100)
            x += selling_pressure
            y = k / x
            y += expected_demand
            x = k / y

        y_diff = abs(y - y_new)
        if y_diff < closest_y_diff:
            closest_y_diff = y_diff
            closest_demand = expected_demand

        if y_diff < tolerance:
            return expected_demand

        initial_expected_demand += (y_new - y) / selected_month
        iteration += 1

    return closest_demand


