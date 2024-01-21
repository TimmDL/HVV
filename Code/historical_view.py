# historical_view.py
import pandas as pd
import plotly.express as px
import streamlit as st
from time_utils import calculate_transition_durations
from predictive_insights import basic_predictive_insights

def create_issue_heat_map(df):
    issue_df = df[df['state'].isin(['OUT_OF_ORDER', 'WARNING'])]
    location_issue_counts = issue_df.groupby(['Latitude', 'Longitude']).size().reset_index(name='issue_count')

    # Calculate average latitude and longitude for centering the map
    avg_latitude = df['Latitude'].mean()
    avg_longitude = df['Longitude'].mean()

    fig = px.density_mapbox(location_issue_counts, lat='Latitude', lon='Longitude', z='issue_count',
                            radius=10, center={"lat": avg_latitude, "lon": avg_longitude}, zoom=10,
                            mapbox_style="open-street-map", color_continuous_scale="phase")
    return fig

def display(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    min_date, max_date = df['Timestamp'].dt.date.min(), df['Timestamp'].dt.date.max()
    selected_date_range = st.date_input("Select date range", [min_date, max_date])

    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]

        col1, col2 = st.columns(2)
        with col1:
            error_warning_df = filtered_df[filtered_df['state'].isin(['WARNING', 'OUT_OF_ORDER'])]
            grouped_trends = error_warning_df.groupby([error_warning_df['Timestamp'].dt.date, 'state']).size().reset_index(name='counts')
            fig_trends = px.line(grouped_trends, x='Timestamp', y='counts', color='state', title='Warning and Out-Of-Order Trends')
            st.plotly_chart(fig_trends)

        with col2:
            avg_durations = calculate_transition_durations(filtered_df, start_date, end_date)
            st.write("Average Durations (hours):")
            for transition, avg_duration in avg_durations.items():
                st.write(f"{transition.replace('_', ' ').title()}: {avg_duration}")

        col3, col4 = st.columns([2, 1])
        with col3:
            pie_chart_df = filtered_df.copy()
            pie_chart_df['state'] = pie_chart_df['state'].replace(['OPERATIONAL', 'IN_OPERATION'], 'OPERATIONAL_STATES')
            state_counts = pie_chart_df['state'].value_counts()
            fig_state_proportion = px.pie(state_counts, names=state_counts.index, values=state_counts, title='State Proportions')
            st.plotly_chart(fig_state_proportion)

        with col4:
            insights = basic_predictive_insights(filtered_df)
            st.write("Predictive Maintenance Insights:")
            for insight in insights:
                st.write(insight)

        st.header("Local Issue Heat Map")
        issue_heat_map = create_issue_heat_map(filtered_df)
        st.plotly_chart(issue_heat_map)

    else:
        st.warning("Please select a start and end date to display the analyses.")

# Example usage
# df = pd.read_csv('path_to_your_data.csv')
# display(df)
