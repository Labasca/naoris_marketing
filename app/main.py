import streamlit as st
from components.charts import plot_supply_shock, create_emissions_chart
from components.widgets import display_widget, display_widget1
from utils.data import get_sheet_data
from utils.helpers import get_image_base64, create_image_html
from config.settings import APP_SETTINGS, SP_OPTIONS, DEFAULT_SP_INDEX

def main():
    # Page config
    st.set_page_config(layout="wide", page_icon="assets/fav_BT.png", page_title="Naoris Marketing")

    # Remove sidebar navigation
    st.markdown("""
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    # Sidebar spacing
    st.sidebar.markdown("\n" * 4)

    # Load data
    data = get_sheet_data(['Database', 'streamlit_emissions'])

    # Sidebar logo and link
    link = 'https://blacktokenomics.com/'
    image_path = "assets/blacktokenomics.png"
    encoded_image = get_image_base64(image_path)
    st.sidebar.markdown(
        f'<a href="{link}" target="_blank"><img src="{encoded_image}" width="300"></a>',
        unsafe_allow_html=True
    )
    st.sidebar.caption("Specialized Tokenomics firm for Web3 Projects, Launchpads, VCs & Funds.")
    st.sidebar.markdown("---")
    st.sidebar.caption(
        "This supply shock and marketing visualizer is based on Uniswap V2 liquidity logic."
    )

    # Sidebar settings
    starting_price = 0.09
    st.sidebar.header("Adjust Settings")

    # Selling Pressure Settings
    with st.sidebar.expander("Selling Pressure Assumptions", expanded=True):
        selling_pressure = st.slider(
            "Selling Pressure (SP)", 
            min_value=0, 
            max_value=100, 
            value=40, 
            step=1,
            help="Set the percentage of tokens that are expected to be sold."
        )
        selling_pressure_source = st.selectbox(
            "Selling Pressure Source", 
            SP_OPTIONS, 
            index=DEFAULT_SP_INDEX,
            help="Set the source of the selling pressure."
        )

    # Temporary Settings
    with st.sidebar.expander("Temporary Settings", expanded=True):
        st.caption(
            'These settings are available temporary to demonstrate the functions of the dashboard, '
            'until the project launches and we can use real time data.'
        )
        st.markdown("---")
        
        st.caption('Select the expected FDV you are planning to have at launch.')
        
        fdv = st.slider(
            "Select Launch FDV",
            min_value=50,
            max_value=5000,
            value=500,
            step=10,
            format="%dM"
        )

        actual_fdv = fdv * 1000000
        starting_price = actual_fdv / 1000000000

        st.caption(
            f'With an FDV of <strong>&#36;{fdv if fdv < 1000 else fdv / 1000}'
            f'{"M" if fdv < 1000 else "B"}</strong>, launch price is going to be '
            f'<strong>&#36;{starting_price:.2f}</strong>',
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        st.caption(
            'Select the speculative month after launch to see the expected selling pressure of that month.'
        )
        selected_month = st.slider('Select a month:', min_value=0, max_value=48, value=0, step=1)

    # Main content
    if 'streamlit_emissions' in data and 'Database' in data:
        try:
            # Process emissions data
            processed_emissions = create_emissions_chart(
                data['streamlit_emissions'],
                data['Database'],
                selling_pressure_source,
                selling_pressure
            )

            if 'Months' in processed_emissions.columns:
                # Display logo
                logo_path = "assets/logo.png"
                logo_base64 = get_image_base64(logo_path)
                html_str = create_image_html(logo_base64, width="450px", height="auto")
                st.markdown(html_str, unsafe_allow_html=True)
                st.markdown("")
                st.markdown("---")

                # Display description
                col1, col2, col3 = st.columns([0.2, 1, 0.2])
                with col2:
                    st.markdown("""
                        <div style="display: flex; justify-content: center; align-items: center; height: 100%; text-align: center;">
                            <div class="bordered-container">
                                <p style="font-size: 18px;">
                                    This simulation will enable the marketing team of Naoris Protocol to better align 
                                    their marketing efforts with token unlock events, ensuring that marketing strategies 
                                    and tokenomics are coordinated.<br><br>
                                    <b>The main goals here are:</b><br><br>
                                    - Use marketing funds in the most effective way.<br><br>
                                    - Avoid sudden price drops when larger token unlocks occur.
                                </p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                # Calculate metrics and create visualizations
                from utils.data import sum_monthly_emissions
                metrics = sum_monthly_emissions(
                    data['streamlit_emissions'],
                    selling_pressure,
                    selected_month,
                    data['Database']
                )
                
                selected_month_emissions_sum, previous_month_emissions_sum, future_month_emissions_sum, \
                selected_month_investor_percent, previous_month_investor_percent, future_month_investor_percent, \
                selected_month_emissions_sum_100SP, previous_month_emissions_sum_100SP, future_month_emissions_sum_100SP = metrics

                plot_supply_shock1, selected_supply_shock, previous_supply_shock, future_supply_shock = \
                    plot_supply_shock(processed_emissions, selected_month)

                # Calculate values
                def calculate_values(emissions_sum, investor_percent):
                    emissions_value = emissions_sum * starting_price
                    investor_value = emissions_value * investor_percent / 100
                    return emissions_value, investor_value

                selected_values = calculate_values(selected_month_emissions_sum, selected_month_investor_percent)
                previous_values = calculate_values(previous_month_emissions_sum, previous_month_investor_percent)
                future_values = calculate_values(future_month_emissions_sum, future_month_investor_percent)

                selected_100sp = calculate_values(selected_month_emissions_sum_100SP, selected_month_investor_percent)
                previous_100sp = calculate_values(previous_month_emissions_sum_100SP, previous_month_investor_percent)
                future_100sp = calculate_values(future_month_emissions_sum_100SP, future_month_investor_percent)

                # Display month labels
                def get_month_display(month):
                    return "TGE" if month == 0 else f"Month {month}"

                month_labels = {
                    'current': get_month_display(selected_month),
                    'previous': get_month_display(selected_month-1),
                    'future': get_month_display(selected_month+1)
                }

                # Display widgets
                st.markdown("")
                col1, col2, col3 = st.columns([0.3, 0.4, 0.3])

                with col1:
                    if previous_supply_shock is not None and previous_values[0] is not None:
                        display_widget1(
                            month_labels['previous'],
                            "Supply Shock (%)", f"{previous_supply_shock:.2f}%",
                            "Unlock Value (SP)", f"${previous_values[0]:,.0f}",
                            "Value for Investors (Max)", f"${previous_100sp[1]:,.0f}",
                            "Value for Investors (SP)", f"${previous_values[1]:,.0f}",
                            "Unlock Value (Max)", f"${previous_100sp[0]:,.0f}"
                        )

                with col2:
                    display_widget(
                        month_labels['current'],
                        "Supply Shock (%)", f"{selected_supply_shock:.2f}%",
                        "Unlock Value (SP)", f"${selected_values[0]:,.0f}",
                        "Value for Investors (Max)", f"${selected_100sp[1]:,.0f}",
                        "Value for Investors (SP)", f"${selected_values[1]:,.0f}",
                        "Unlock Value (Max)", f"${selected_100sp[0]:,.0f}"
                    )
                    st.markdown("")

                with col3:
                    display_widget1(
                        month_labels['future'],
                        "Supply Shock (%)", f"{future_supply_shock:.2f}%",
                        "Unlock Value (SP)", f"${future_values[0]:,.0f}",
                        "Value for Investors (Max)", f"${future_100sp[1]:,.0f}",
                        "Value for Investors (SP)", f"${future_values[1]:,.0f}",
                        "Unlock Value (Max)", f"${future_100sp[0]:,.0f}"
                    )

                # Display supply shock chart
                st.markdown("---")
                st.markdown(
                    "<h3 style='text-align: center; font-size: 22px;'>Monthly Supply Shock Scale</h3>",
                    unsafe_allow_html=True
                )
                st.markdown("")
                st.plotly_chart(plot_supply_shock1, use_container_width=True, config={"displayModeBar": False})

            else:
                st.error("Months column not found in the emissions data.")

        except ValueError as e:
            st.error(f"Data processing error: {e}")

if __name__ == "__main__":
    main()