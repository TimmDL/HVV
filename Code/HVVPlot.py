import pandas as pd
import plotly.express as px
import streamlit as st

# Read the CSV file
df = pd.read_csv('Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]

# Function to calculate size based on the state
def calculate_size(state):
    if state not in ['OPERATIONAL', 'IN_OPERATION']:
        return 20  # Size for broken machines
    return 10  # Size for operational machines

# Prepare the data for plotting
grouped = recent_stations.groupby(['HstName', 'state']).apply(lambda x: pd.Series({
    'Size': calculate_size(x['state'].iloc[0]),
    'Latitude': x['Latitude'].iloc[0],
    'Longitude': x['Longitude'].iloc[0]
})).reset_index()

# Create the scatter plot
fig = px.scatter_mapbox(grouped,
                        lat="Latitude",
                        lon="Longitude",
                        color='state',  # Color by state
                        size='Size',  # Size by the calculated value
                        hover_data=['HstName', 'state'],
                        zoom=12,
                        mapbox_style="open-street-map")

# Update the layout to show the legend
fig.update_layout(
    legend_title_text='State',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01
    )
)

# Display the map in Streamlit
st.plotly_chart(fig)
