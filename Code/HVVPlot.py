import pandas as pd
import plotly.express as px
import streamlit as st

# Read the CSV file
df = pd.read_csv('Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]

# Define color for stations based on the worst machine state
color_scale = {
    'broken': 'red',
    'warning': 'yellow',
    'operational': 'blue'
}

def aggregate_info(group):
    total_machines = len(group)
    broken_machines = sum(state == 'OUT_OF_ORDER' for state in group['state'])
    warning_machines = sum(state == 'WARNING' for state in group['state'])
    size = 2 + (broken_machines + warning_machines) / total_machines * 20
    info = "<br>".join([f"Machine {row['Automatennr']}: {row['state']}" for _, row in group.iterrows()])

    if broken_machines > 0:
        color = 'broken'
    elif warning_machines > 0 and broken_machines == 0:  # Ensure no broken machines are present
        color = 'warning'
    else:
        color = 'operational'
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
                        color_discrete_map=color_scale,
                        size_max=30,  # Adjust the maximum size as needed
                        zoom=12,
                        mapbox_style="open-street-map")

# Display the map in Streamlit
st.plotly_chart(fig)
