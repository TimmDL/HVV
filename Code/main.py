import streamlit as st
import pandas as pd
import current_view
import historical_view

# Set the page to wide mode
st.set_page_config(layout="wide")

# Add title and description
st.title('**Dashboard: Maintenance Status of the SSTs**')
st.write('Description of the dashboard. Explains what it does, how to use it, etc.')

# Read the CSV file
df = pd.read_csv('/Users/timmdill/Documents/GitHub/HVV/Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Radio button for selecting the view mode
view_mode = st.radio("Select View Mode:", ('Current Data View', 'Historical Data View'))

if view_mode == 'Current Data View':
    current_view.display(df)
elif view_mode == 'Historical Data View':
    historical_view.display(df)  # Pass df as an argument
