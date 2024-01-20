import pandas as pd
import plotly.express as px
import streamlit as st
from time_utils import calculate_downtime
import time_utils


def display(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Find the minimum and maximum dates in the dataset
    min_date, max_date = df['Timestamp'].dt.date.min(), df['Timestamp'].dt.date.max()

    # Streamlit date range picker with default values set to min and max dates
    selected_date_range = st.date_input("Select date range", [min_date, max_date])

    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]

        # Calculate downtime using time_utils
        downtime_df = calculate_downtime(filtered_df, 'WARNING', 'OUT_OF_ORDER')

        # Plotting downtime (adjust the plot logic as per your requirements)
        fig = px.timeline(downtime_df, x_start='Timestamp', x_end='End_Timestamp', y='LmuId', labels={'LmuId': 'Machine ID'})
        fig.update_layout(xaxis_title='Time', yaxis_title='Machine ID', title='Machine Downtime Analysis')
        st.plotly_chart(fig)

# Example usage
# df = pd.read_csv('path_to_your_data.csv')  # Replace with your actual data path
# display(df)  # Uncomment for testing
