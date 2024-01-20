import pandas as pd
import plotly.express as px
import streamlit as st

# Configure the page to wide layout
st.set_page_config(layout="wide")

# Add title and description to the dashboard
st.title('**Dashboard: Maintenance Status of the SSTs**')
st.write('This dashboard provides an overview of the maintenance status of SSTs, '
         'including current and historical data views.')

# Read the CSV file containing SST data
df = pd.read_csv('/Users/timmdill/Documents/GitHub/HVV/Data/sst_alldata.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Radio button for selecting the view mode (current or historical data)
view_mode = st.radio("Select View Mode:", ('Current Data View', 'Historical Data View'))


# Define a function for spaceless search in dataframes
def spaceless_search(search_query, dataframe):
    """ Perform a spaceless search in the dataframe based on the search query. """

    def remove_spaces(text_input):
        """ Remove all spaces from a given string. """
        return ''.join(text_input.split())

    # Normalize the search query by removing spaces and converting to lowercase
    normalized_query = remove_spaces(search_query.lower())

    def contains_query(row):
        """ Check if the normalized query is in the row data. """
        row_string = remove_spaces(' '.join(map(str, row)).lower())
        return normalized_query in row_string

    # Return the filtered dataframe based on the search query
    return dataframe[dataframe.apply(contains_query, axis=1)]


# Define color mapping for station status
color_scale = {
    'broken': 'red',
    'warning': '#FFA15A',
    'operational': 'blue',
    'error_resource': '#FF6692',
}


# Function to create an aggregated view for current data
def create_aggregated_view(stations):
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

    grouped = stations.groupby('HstName').apply(aggregate_info).reset_index()
    grouped[['Machine_Info', 'Station_Status', 'Size']] = pd.DataFrame(grouped[0].tolist(), index=grouped.index)
    grouped.drop(columns=[0], inplace=True)

    station_coordinates = stations[['HstName', 'Latitude', 'Longitude']].drop_duplicates()
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


# Process and display data based on the selected view mode
if view_mode == 'Current Data View':
    st.header("Current Data Analysis")
    stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]
    create_aggregated_view(stations)  # Correctly pass stations as an argument

elif view_mode == 'Historical Data View':
    st.header("Historical Data Analysis")
    stations = df  # Use entire dataset for historical view
    create_aggregated_view(stations)  # Correctly pass stations as an argument


# Search bar for filtering data
search_query = st.text_input("Search:", "").strip()

# Apply filters based on states
filtered_states = []
if show_out_of_order:
    filtered_states.append('OUT_OF_ORDER')
if show_warning:
    filtered_states.append('WARNING')
if show_operational:
    filtered_states.append('OPERATIONAL')
if show_resource:
    filtered_states.append('ERROR_RESOURCE')

# Check if no checkboxes are selected
if not filtered_states:
    st.warning("Please select at least one state to display the data.")
    filtered_df = pd.DataFrame()
else:
    # Apply state filters to the DataFrame
    filtered_df = stations[stations['state'].isin(filtered_states)]

    # Apply the spaceless search if there is a search query
    if search_query:
        filtered_df = spaceless_search(search_query, filtered_df)

        # Check if the filtered dataframe is empty after applying the search
        if filtered_df.empty:
            st.warning("No results found for your search query.")

# Display the dataframe only if it is not empty
if not filtered_df.empty:
    # Apply selected columns to the DataFrame
    filtered_df = filtered_df[selected_columns]

    # Display the filtered DataFrame
    st.dataframe(filtered_df)

# Column toggle and state filtering logic
desired_order = ['Timestamp', 'state', 'LmuId', 'HstName', 'Standplatz', 'Linie',
                 'LmuState', 'AlarmState', 'CompType', 'CompNr', 'prevState',
                 'comment', 'Automatennr', 'EVU / Bereich', 'Status Gerät', 'Latitude', 'Longitude']

# Column toggle
available_columns = stations.columns.tolist()
selected_columns = st.multiselect("Select columns to display:", available_columns, default=desired_order)
