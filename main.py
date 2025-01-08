import streamlit as st
import pandas as pd
import os
from utilities import get_image_base64, display_widget, display_widget1, create_image_html, get_image_as_base64
from data_loader import get_sheet_data
from selling_pressure import create_emissions_chart, sum_monthly_emissions
from v2_liquidity import plot_supply_shock

st.set_page_config(layout="wide", page_icon="fav_BT.png", page_title="Naoris Marketing")


def main():

    no_sidebar_style = """
        <style>
            div[data-testid="stSidebarNav"] {display: none;}
        </style>
    """

    st.markdown(no_sidebar_style, unsafe_allow_html=True)
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")
    st.sidebar.markdown("")

    # Assuming the sheet names are 'Database' and 'streamlit_emissions'
    data = get_sheet_data(['Database', 'streamlit_emissions'])
    # The data is retrieved but not displayed


    SP_options = ["Unlocks", "Circulation"]
    default_index = SP_options.index("Circulation")  # Get the index of 'Circulation' in the list


    link = 'https://blacktokenomics.com/'
    image_path = "blacktokenomics.png"  # Update to the correct path if different

    encoded_image = get_image_as_base64(image_path)
    st.sidebar.markdown(f'<a href="{link}" target="_blank"><img src="{encoded_image}" width="300"></a>',
                        unsafe_allow_html=True)

    st.sidebar.caption("Specialized Tokenomics firm for Web3 Projects, Launchpads, VCs & Funds.")

    st.sidebar.markdown("---")

    st.sidebar.caption(
        "This supply shock and marketing visualizer is based on Uniswap V2 liquidity logic.")



    starting_price = 0.09

    st.sidebar.header("Adjust Settings")

    with st.sidebar.expander("Selling Pressure Assumptions", expanded=True):
        selling_pressure = st.slider("Selling Pressure (SP)", min_value=0, max_value=100, value=40, step=1,
                                        help="Set the precentage of tokens that are expected to be sold.")
        selling_pressure_source = st.selectbox("Selling Pressure Source", SP_options, index=default_index,
                                                help="""Set the source of the selling pressure.""")

    with st.sidebar.expander("Temporary Settings", expanded=True):

        st.caption(
            f'These settings are available temporary to demonstrate the functions of the dashboard, until the project launches and we can use real time data.',
            unsafe_allow_html=True)

        st.markdown("---")

        st.caption(
            f'Select the expected FDV you are planing to have at launch.',
            unsafe_allow_html=True)

        fdv = st.slider("Select Launch FDV",
                        min_value=50,
                        max_value=5000,
                        value=500,  # Default value set to the minimum value
                        step=10,
                        format="%dM")


        actual_fdv = fdv * 1000000
        starting_price = actual_fdv / 1000000000

        st.caption(
            f'With an FDV of <strong>&#36;{fdv if fdv < 1000 else fdv / 1000}{"M" if fdv < 1000 else "B"}</strong>, launch price is going to be <strong>&#36;{starting_price:.2f}</strong>',
            unsafe_allow_html=True)

        st.markdown("---")

        st.caption(
            f'Select the speculative month after launch to see the expected selling pressure of that month.',
            unsafe_allow_html=True)

        selected_month = st.slider('Select a month:', min_value=0, max_value=48, value=0, step=1)

    # Data Processing
    if 'streamlit_emissions' in data and 'Database' in data:
        try:
            processed_emissions = create_emissions_chart(
                data['streamlit_emissions'], data['Database'], selling_pressure_source, selling_pressure
            )

            

            if 'Months' in processed_emissions.columns:

                current_dir = os.path.dirname(__file__)  # Get the directory of the current file
                image_path = os.path.join(current_dir,
                                            "logo.png")  # Construct the image file path

                # Convert the image to a base64 string
                image_base64 = get_image_base64(image_path)

                # Specify your desired image dimensions
                desired_width = "450px"  # Set width as you like (e.g., '300px', '50%', etc.)
                desired_height = "auto"  # Use 'auto' to maintain aspect ratio, or set a specific height

                # Create the HTML string with the embedded image and specified dimensions
                html_str = create_image_html(image_base64, width=desired_width, height=desired_height)

                # Use Streamlit to display the HTML
                st.markdown(html_str, unsafe_allow_html=True)
                st.markdown("")



                st.markdown("---")

                col1, col2, col3 = st.columns([0.2, 1, 0.2])

                with col2:
                    st.markdown("""
                    <div style="display: flex; justify-content: center; align-items: center; height: 100%; text-align: center;">
                        <div class="bordered-container">
                            <p style="font-size: 18px;">
                                This simulation will enable the marketing team of Naoris Protocol to better align their marketing efforts with token unlock events, ensuring that marketing strategies and tokenomics are coordinated.<br><br>
                                <b>The main goals here are:</b><br><br>
                                - Use marketing funds in the most effective way.<br><br>
                                - Avoid sudden price drops when larger token unlocks occur.
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("---")

                selected_month_emissions_sum, previous_month_emissions_sum, future_month_emissions_sum, selected_month_investor_percent, previous_month_investor_percent, future_month_investor_percent, selected_month_emissions_sum_100SP, previous_month_emissions_sum_100SP, future_month_emissions_sum_100SP = sum_monthly_emissions(data['streamlit_emissions'], selling_pressure, selected_month, data['Database'])

                plot_supply_shock1, selected_supply_shock, previous_supply_shock, future_supply_shock = plot_supply_shock(processed_emissions, selected_month)

                selected_month_emissions_value=selected_month_emissions_sum * starting_price
                selected_month_investor_value=selected_month_emissions_value*selected_month_investor_percent/100

                previous_month_emissions_value = previous_month_emissions_sum * starting_price
                previous_month_investor_value = previous_month_emissions_value * previous_month_investor_percent / 100

                future_month_emissions_value = future_month_emissions_sum * starting_price
                future_month_investor_value = future_month_emissions_value * future_month_investor_percent / 100

                def get_month_display(selected_month):
                    if selected_month == 0:
                        return "TGE"
                    else:
                        return f"Month {selected_month}"

                selected_month_current=get_month_display(selected_month)
                selected_month_previous=get_month_display(selected_month-1)
                selected_month_future=get_month_display(selected_month+1)

                selected_month_investor_value_100 = selected_month_emissions_sum_100SP*selected_month_investor_percent/100*starting_price
                previous_month_investor_value_100 = previous_month_emissions_sum_100SP*previous_month_investor_percent/100*starting_price
                future_month_investor_value_100 = future_month_emissions_sum_100SP*future_month_investor_percent/100*starting_price

                selected_month_total_value_100 = selected_month_emissions_sum_100SP * starting_price
                previous_month_total_value_100 = previous_month_emissions_sum_100SP * starting_price
                future_month_total_value_100 = future_month_emissions_sum_100SP * starting_price

                st.markdown("")

                col1, col2, col3 = st.columns([0.3, 0.4, 0.3])

                with col1:
                    # Check if the necessary data is available before trying to format it
                    if previous_supply_shock is not None and previous_month_emissions_value is not None and previous_month_investor_percent is not None and previous_month_investor_value is not None:
                        display_widget1(
                            f'{selected_month_previous}',
                            "Supply Shock (%)",
                            f"{previous_supply_shock:.2f}%",
                            "Unlock Value (SP)",
                            f"${previous_month_emissions_value:,.0f}",
                            "Value for Investors (Max)",
                            f"${previous_month_investor_value_100:,.0f}",
                            "Value for Investors (SP)",
                            f"${previous_month_investor_value:,.0f}",
                            "Unlock Value (Max)",
                            f"${previous_month_total_value_100:,.0f}"
                        )
                    else:
                        # Here you can decide to display nothing or display some default or error message
                        # For example, you might display a message indicating data is unavailable
                        st.markdown("")

                with col2:

                    display_widget(f'{selected_month_current}', "Supply Shock (%)", f"{selected_supply_shock:.2f}%", "Unlock Value (SP)", f"${selected_month_emissions_value:,.0f}", "Value for Investors (Max)", f"${selected_month_investor_value_100:,.0f}", "Value for Investors (SP)", f"${selected_month_investor_value:,.0f}","Unlock Value (Max)", f"${selected_month_total_value_100:,.0f}")
                    st.markdown("")


                with col3:
                    display_widget1(f'{selected_month_future}', "Supply Shock (%)", f"{future_supply_shock:.2f}%", "Unlock Value (SP)",
                                    f"${future_month_emissions_value:,.0f}", "Value for Investors (Max)",
                                    f"${future_month_investor_value_100:,.0f}", "Value for Investors (SP)",
                                    f"${future_month_investor_value:,.0f}",
                                    "Unlock Value (Max)",
                                    f"${future_month_total_value_100:,.0f}"
                                    )

                st.markdown("---")

                st.markdown(
                    "<h3 style='text-align: center; font-size: 22px;'>Monthly Supply Shock Scale</h3>",
                    unsafe_allow_html=True)
                st.markdown("")

                st.plotly_chart(plot_supply_shock1, use_container_width=True, config={"displayModeBar": False})


            else:
                st.error("Months column not found in the emissions data.")

        except ValueError as e:
            st.error(f"Data processing error: {e}")

if __name__ == "__main__":
        main()
