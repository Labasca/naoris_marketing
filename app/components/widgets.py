import streamlit as st

def display_widget(title, label1, value1, label2, value2, label3, value3, label4, value4, label5, value5,
                   title_color="white", label_color="#afb2b6", value_color="white",
                   title_font_size="35px", label_font_size="12px", value_font_size="20px",
                   label_margin_bottom="-7px", value_margin_top="0px", box_width="95%",
                   box_height="auto", box_padding_top="12px", small_box_padding_bottom="10px",
                   box_padding_lr="12px", box_background_color="#16171d",
                   box_border_radius="15px", box_border_color="#3d4044", box_background_color1="#262730",
                   box_border_width="2px"):
    metric_html = f"""
        <div style="width: {box_width}; height: {box_height}; margin: auto; text-align: center; padding: {box_padding_top} {f'5px'} {f'13px'} {f'5px'}; background-color: {box_background_color}; border-radius: {box_border_radius}; border: {box_border_width} solid {box_border_color};">
            <div style="color: {title_color}; font-size: {title_font_size}; margin-bottom: 10px;">{title}</div>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1; min-width: 100%;">{display_large_metric_content(label1, value1, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, f'97%', box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            </div>
            <div style="height: 10px;"></div>
            <div style="display: flex; justify-content: space-between;">
            <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label2, value2, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label5, value5, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div></div>
            <div style="height: 10px;"></div>
            <div style="display: flex; justify-content: space-between;">
            <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label4, value4, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label3, value3, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div></div>
        </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)

def display_widget1(title, label1, value1, label2, value2, label3, value3, label4, value4, label5, value5,
                   title_color="white", label_color="#afb2b6", value_color="white",
                   title_font_size="35px", label_font_size="12px", value_font_size="20px",
                   label_margin_bottom="-7px", value_margin_top="0px", box_width="95%",
                   box_height="auto", box_padding_top="12px", small_box_padding_bottom="10px",
                   box_padding_lr="12px", box_background_color="#16171d",
                   box_border_radius="15px", box_border_color="#3d4044", box_background_color1="#262730",
                   box_border_width="2px", opacity=50, scale=90):
    # Convert opacity to a CSS-compatible format
    opacity_value = opacity / 100

    # Adjust the scaling factor from percentage to CSS scale transform value
    scale_value = scale / 100

    # Include the opacity and scale in the style
    wrapper_style = f"opacity: {opacity_value}; transform: scale({scale_value}); transition: opacity 0.5s, transform 0.5s;"

    metric_html = f"""
        <div style="width: {box_width}; height: {box_height}; margin: auto; text-align: center; padding: {box_padding_top} {f'5px'} {f'13px'} {f'5px'}; background-color: {box_background_color}; border-radius: {box_border_radius}; border: {box_border_width} solid {box_border_color}; {wrapper_style}">
            <div style="color: {title_color}; font-size: {title_font_size}; margin-bottom: 10px;">{title}</div>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1; min-width: 100%;">{display_large_metric_content(label1, value1, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, f'97%', box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            </div>
            <div style="height: 10px;"></div>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label2, value2, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
                <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label5, value5, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            </div>
            <div style="height: 10px;"></div>
            <div style="display: flex; justify-content: space-between;">
                <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label4, value4, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
                <div style="flex: 1; min-width: 45%;">{display_large_metric_content(label3, value3, label_color, value_color, label_font_size, value_font_size, label_margin_bottom, value_margin_top, box_width, box_height, box_padding_top, small_box_padding_bottom, box_padding_lr, box_background_color1, box_border_radius, box_border_color, box_border_width)}</div>
            </div>
        </div>
    """
    st.markdown(metric_html, unsafe_allow_html=True)

def display_large_metric_content(label, value, label_color="#afb2b6", value_color="white",
                                 label_font_size="22px", value_font_size="35px",
                                 label_margin_bottom="0px", value_margin_top="0px",
                                 box_width="90%", box_height="auto", box_padding_top="12px",
                                 box_padding_bottom="7px", box_padding_lr="30px",
                                 box_background_color="#226567", box_border_radius="15px",
                                 box_border_color="#1d4044", box_border_width="1px"):
    return f"""
        <div style="width: {box_width}; height: {box_height}; margin: auto; text-align: center; padding: {box_padding_top} {box_padding_lr} {box_padding_bottom} {box_padding_lr}; background-color: {box_background_color}; border-radius: {box_border_radius}; border: {box_border_width} solid {box_border_color};">
            <div style="margin: {value_margin_top} 0 {label_margin_bottom} 0; color: {label_color}; font-size: {label_font_size};">{label}</div>
            <div style="margin-top: 5px; padding-top: 5px; color: {value_color}; font-size: {value_font_size};">{value}</div>
        </div>
    """