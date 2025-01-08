import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json
import os

# Get the directory of the current script to ensure file paths are relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Function to extract sheet ID from URL
def extract_sheet_id(url):
    parts = url.split('/')
    try:
        return parts[5]
    except IndexError:
        return None

# Function to save data to a JSON file, adjusted to use script_dir
def save_data_to_file(data, filename):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f)

# Function to load data from a JSON file, adjusted to use script_dir
def load_data_from_file(filename):
    filepath = os.path.join(script_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        return None  # Return None or handle as needed if the file doesn't exist

# Access spreadsheet function remains unchanged
@st.cache_data(ttl=None, hash_funcs={gspread.client.Client: lambda _: None})
def access_spreadsheet(sheet_id):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('investorstreamlit-45b79cc49b34.json', scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open_by_key(sheet_id)
        return sheet
    except Exception as e:
        return str(e)

# Adjusted get_sheet_data function, now with file path adjustments for caching
@st.cache_data(ttl=None, hash_funcs={gspread.client.Client: lambda _: None})
def get_sheet_data(_sheet, sheet_names, sheet_id, use_files=True):
    filenames = {
        'Database': 'Database.json',
        'streamlit_emissions': 'streamlit_emissions.json'
    }
    data = {}
    for name in sheet_names:
        filename = filenames.get(name)
        filepath = os.path.join(script_dir, filename)
        if use_files and os.path.exists(filepath):
            data[name] = load_data_from_file(filename)
        else:
            try:
                sheet_data = _sheet.worksheet(name).get_all_records()
                data[name] = sheet_data
                save_data_to_file(sheet_data, filename)
            except Exception as e:
                data[name] = f"Error reading sheet {name}: {str(e)}"
    return data
