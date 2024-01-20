import pandas as pd
import plotly.express as px
import streamlit as st

# Set the page to wide mode
st.set_page_config(layout="wide")

# Add title and description
st.title('**Dashboard: Maintenance Status of the SSTs**')
st.write('Description of the dashboard. Explains what it does, how to use it, etc.')

# Read the CSV file
df = pd.read_csv('Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]

# Define color for stations based on the simplified machine state
color_scale = {
    'broken': 'red',
    'warning': '#FFA15A',
    'operational': 'blue',
    'error_resource': '#FF6692',
}


# Function to create aggregated view
def create_aggregated_view():
    def aggregate_info(group):
        total_machines = len(group)
        broken_machines = sum(state == 'OUT_OF_ORDER' for state in group['state'])
        warning_machines = sum(state == 'WARNING' for state in group['state'])
        resource_machines = sum(state == 'ERROR_RESOURCE' for state in group['state'])
        size = 2 + (broken_machines + warning_machines + resource_machines) / total_machines * 20
        machine_details = "<br>".join([
            f"LmuId: {row['LmuId']}, State: {row['state']}, Linie: {row['Linie']}" +
            (f", Standplatz: {row['Standplatz']}" if pd.notna(row['Standplatz']) else "")
            for _, row in group.iterrows()
        ])
        color = 'operational'
        if broken_machines > 0:
            color = 'broken'
        elif warning_machines > 0:
            color = 'warning'
        elif resource_machines > 0:
            color = 'error_resource'

        # Adding a line break after Machine_Info
        return f"{machine_details}<br>", color, size

    grouped = recent_stations.groupby('HstName').apply(aggregate_info).reset_index()
    grouped[['Machine_Info', 'Station_Status', 'Size']] = pd.DataFrame(grouped[0].tolist(), index=grouped.index)
    grouped.drop(columns=[0], inplace=True)

    station_coordinates = recent_stations[['HstName', 'Latitude', 'Longitude']].drop_duplicates()
    grouped = pd.merge(grouped, station_coordinates, on='HstName', how='left')

    fig = px.scatter_mapbox(grouped,
                            lat="Latitude",
                            lon="Longitude",
                            color='Station_Status',
                            color_discrete_map=color_scale,
                            hover_name='HstName',
                            hover_data={'Machine_Info': True},
                            size='Size',
                            size_max=30,
                            zoom=11,
                            mapbox_style="open-street-map")

    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)


# Display scatter_mapbox
create_aggregated_view()


# Define the space removal function
def remove_spaces(text_input):
    return ''.join(text_input.split())


# Define the spaceless search function
def spaceless_search(search_query, dataframe):
    # Remove spaces from the search query
    normalized_query = remove_spaces(search_query.lower())

    def contains_query(row):
        # Remove spaces and lowercase row data before comparison
        row_string = remove_spaces(' '.join(map(str, row)).lower())
        return normalized_query in row_string

    return dataframe[dataframe.apply(contains_query, axis=1)]


# Search bar and column toggle
search_query = st.text_input("Search:", "").strip()

# Specify desired column order
desired_order = ['Timestamp', 'state', 'LmuId', 'HstName', 'Standplatz', 'Linie',
                 'LmuState', 'AlarmState', 'CompType', 'CompNr', 'prevState',
                 'comment', 'Automatennr', 'EVU / Bereich', 'Status Gerät', 'Latitude', 'Longitude']

# Column toggle
available_columns = recent_stations.columns.tolist()
selected_columns = st.multiselect("Select columns to display:", available_columns, default=desired_order)

# Filter Table by State
st.write("Filter Table by State:")
show_out_of_order = st.checkbox('Show Out of Order', True)
show_warning = st.checkbox('Show Warning', True)
show_resource = st.checkbox('Show missing resources', True)
show_operational = st.checkbox('Show Operational', False)

filtered_states = []
if show_out_of_order:
    filtered_states.append('OUT_OF_ORDER')
if show_warning:
    filtered_states.append('WARNING')
if show_operational:
    filtered_states.append('OPERATIONAL')
    filtered_states.append('IN_OPERATION')
if show_resource:
    filtered_states.append('ERROR_RESOURCE')

# Check if no checkboxes are selected
if not filtered_states:
    st.warning("Please select at least one option to display the data.")
else:
    filtered_df = recent_stations[recent_stations['state'].isin(filtered_states)]

    if search_query:
        filtered_df = spaceless_search(search_query, filtered_df)

    filtered_df = filtered_df[selected_columns]

    # Apply the selected order to the dataframe for display
    filtered_df = filtered_df[selected_columns]

    # Display the filtered dataframe
    st.dataframe(filtered_df)
