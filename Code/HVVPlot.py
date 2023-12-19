import pandas as pd
import plotly.express as px
import streamlit as st

# Read the CSV file
df = pd.read_csv('/Users/timmdill/Downloads/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]

# Define color for stations with broken machines
color_scale = {
    'broken': 'red',  # Color for stations with any broken machine
    'operational': 'blue'  # Color for fully operational stations
}

# Function to aggregate machine information and calculate size for each station
def aggregate_info(group):
    total_machines = len(group)
    broken_machines = sum(state not in ['OPERATIONAL', 'IN_OPERATION'] for state in group['state'])
    broken_ratio = broken_machines / total_machines if total_machines > 0 else 0
    size = 2 + broken_ratio * 20
    info = "<br>".join([f"Machine {row['Automatennr']}: {row['state']}" for _, row in group.iterrows()])
    color = 'broken' if broken_machines > 0 else 'operational'
    return info, color, size

# Group by 'HstName' and aggregate data
grouped = recent_stations.groupby('HstName').apply(lambda x: pd.Series({
    'Machine_Info': aggregate_info(x)[0],
    'Station_Color': aggregate_info(x)[1],
    'Size': aggregate_info(x)[2],
    'Latitude': x['Latitude'].iloc[0],
    'Longitude': x['Longitude'].iloc[0]
})).reset_index()

# Create the scatter map
fig = px.scatter_mapbox(grouped,
                        hover_name='HstName',
                        hover_data=['Machine_Info'],
                        lat="Latitude",
                        lon="Longitude",
                        color='Station_Color',
                        size='Size',
                        color_discrete_map={
                            'broken': 'red',
                            'operational': 'blue'
                        },
                        size_max=30,  # Adjust the maximum size as needed
                        zoom=12,
                        mapbox_style="open-street-map")

# Display the map in Streamlit
st.plotly_chart(fig)