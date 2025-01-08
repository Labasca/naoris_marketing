import streamlit as st
import json
import os

# Get the directory of the current script to ensure file paths are relative to this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Function to save data to a JSON file
def save_data_to_file(data, filename):
    filepath = os.path.join(script_dir, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f)

# Function to load data from a JSON file
@st.cache_data
def load_data_from_file(filename):
    filepath = os.path.join(script_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        return None

# Function to get data from JSON files
@st.cache_data
def get_sheet_data(sheet_names):
    filenames = {
        'Database': 'Database.json',
        'streamlit_emissions': 'streamlit_emissions.json'
    }
    data = {}
    for name in sheet_names:
        filename = filenames.get(name)
        data[name] = load_data_from_file(filename)
    return data