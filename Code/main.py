import streamlit as st
import pandas as pd
import current_view
import historical_view

# Set the page to wide mode
st.set_page_config(layout="wide")

# Add title and description
st.title('**Dashboard: Maintenance Status of the SSTs**')
st.write('**Choose Your View:** Switch between monitoring the current service status of SSTs and delving into historical'
         ' error analysis. Make your selection to either get real-time insights into the operational health of SSTs or '
         'to investigate past error trends for a deeper understanding of long-term performance and reliability.')

# Read the CSV file
df = pd.read_csv('Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Radio button for selecting the view mode
view_mode = st.radio("Select View Mode:", ('Current Data View', 'Historical Data View'))

# Pass df as an argument for selected view mode
if view_mode == 'Current Data View':
    current_view.display(df)
elif view_mode == 'Historical Data View':
    historical_view.display(df)
