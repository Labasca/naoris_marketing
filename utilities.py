import base64
import pandas as pd
import streamlit as st

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string

def create_image_html(base64_string, width='auto', height='auto'):
    return f"""
    <div style="display:flex;justify-content:center;">
        <img src="data:image/png;base64,{base64_string}" style="width:{width};height:{height};max-width:100%;">
    </div>
    """

def get_image_as_base64(url):
    with open(url, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return "data:image/png;base64," + encoded_string





def human_format(num):
    magnitude = 0
    sign = '-' if num < 0 else ''
    num = abs(num)
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return f'{sign}${num:.2f}{["", "K", "M", "B", "T"][magnitude]}'


def human_format1(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{:.2f}{}'.format(num, ['', 'K', 'M', 'B'][magnitude])


def make_unicode_bold(text):
    # Convert each character to its bold Unicode equivalent if possible
    bold_chars = {c: chr(0x1D400 + ord(c) - ord('A')) for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
    bold_chars.update({c: chr(0x1D41A + ord(c) - ord('a')) for c in 'abcdefghijklmnopqrstuvwxyz'})
    return ''.join(bold_chars.get(c, c) for c in text)

def round_to_nearest(value, nearest):
    return round(value / nearest) * nearest

def custom_price_format(num):
    if num < 0.0000001:
        return f"${num:.9f}".rstrip('0').rstrip('.')
    elif num < 0.000001:
        return f"${num:.8f}".rstrip('0').rstrip('.')
    elif num < 0.00001:
        return f"${num:.7f}".rstrip('0').rstrip('.')
    elif num < 0.0001:
        return f"${num:.6f}".rstrip('0').rstrip('.')
    elif num < 0.001:
        return f"${num:.5f}".rstrip('0').rstrip('.')
    elif num < 0.01:
        return f"${num:.4f}"
    elif num < 0.1:
        return f"${num:.3f}"
    elif num < 1:
        return f"${num:.2f}"
    else:
        return f"${num:.2f}"




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


