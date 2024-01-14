import pandas as pd
import plotly.express as px
import streamlit as st

# Set the page to wide mode
st.set_page_config(layout="wide")

# Add title and description
st.title('**Your Dashboard Title**')
st.write('Description of the dashboard. Explains what it does, how to use it, etc.')

# Read the CSV file
df = pd.read_csv('Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]

# Define color for stations based on the simplified machine state
color_scale = {
    'broken': 'red',
    'warning': '#FFA15A',
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
    'Station_Status': aggregate_info(x)[1],
    'Size': aggregate_info(x)[2],
    'Latitude': x['Latitude'].iloc[0],
    'Longitude': x['Longitude'].iloc[0]
})).reset_index()

# Checkbox for showing all LMU states
show_all_states = st.checkbox('Show all LMU states')
if show_all_states:
    # Plotting all states
    fig_all_states = px.scatter_mapbox(recent_stations,
                                       lat="Latitude",
                                       lon="Longitude",
                                       color='state',  # Automatically assign colors
                                       hover_name='HstName',
                                       hover_data={'HstName': True, 'LmuId': True, 'Linie': True, 'Standplatz': True},
                                       size_max=30,
                                       zoom=12,
                                       mapbox_style="open-street-map")
    fig_all_states.update_layout(height=600)
    st.plotly_chart(fig_all_states, use_container_width=True)

else:
    # Existing logic for simplified view
    grouped = recent_stations.groupby('HstName').apply(lambda x: pd.Series({
        'Machine_Info': aggregate_info(x)[0],
        'Station_Status': aggregate_info(x)[1],
        'Size': aggregate_info(x)[2],
        'Latitude': x['Latitude'].iloc[0],
        'Longitude': x['Longitude'].iloc[0]
    })).reset_index()

    fig = px.scatter_mapbox(grouped,
                            lat="Latitude",
                            lon="Longitude",
                            color='Station_Status',
                            size='Size',
                            color_discrete_map=color_scale,
                            size_max=30,
                            zoom=12,
                            mapbox_style="open-street-map")
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# Search bar and column toggle
search_query = st.text_input("Search:", "").lower()

# Specify desired column order
desired_order = ['Timestamp', 'state', 'LmuId', 'HstName', 'Standplatz', 'Linie',
                 'LmuState', 'AlarmState', 'CompType', 'CompNr', 'prevState',
                 'comment', 'Automatennr', 'EVU / Bereich', 'Status Gerät','Latitude', 'Longitude']

# Column toggle
available_columns = recent_stations.columns.tolist()
selected_columns = st.multiselect("Select columns to display:", available_columns, default=desired_order)

# Filter Table by State
st.write("Filter Table by State:")
show_out_of_order = st.checkbox('Show Out of Order', True)
show_warning = st.checkbox('Show Warning', True)
show_operational = st.checkbox('Show Operational', False)

filtered_states = []
if show_out_of_order:
    filtered_states.append('OUT_OF_ORDER')
if show_warning:
    filtered_states.append('WARNING')
if show_operational:
    filtered_states.append('OPERATIONAL')

filtered_df = recent_stations[recent_stations['state'].isin(filtered_states)]
filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(search_query).any(), axis=1)]
filtered_df = filtered_df[selected_columns]

# Apply the selected order to the dataframe for display
filtered_df = filtered_df[selected_columns]

# Display the filtered dataframe
st.dataframe(filtered_df)
