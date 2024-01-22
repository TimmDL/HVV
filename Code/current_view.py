import pandas as pd
import plotly.express as px
import streamlit as st
import search_utils

# Define color scale for stations
color_scale = {
    'broken': 'red',
    'warning': '#FFA15A',
    'operational': 'blue',
    'error_resource': '#FF6692',
}


# Function to create aggregated view (map with the most recent states)
def create_aggregated_view(recent_stations):
    def aggregate_info(group):
        total_machines = len(group)
        non_operational_machines = sum(state not in ['OPERATIONAL', 'IN_OPERATION'] for state in group['state'])

        # Calculate the importance value
        importance = (non_operational_machines / total_machines) * 100 if total_machines > 0 else 0

        # Determine size based on non-operational machines, with a base size of 2
        size = 2 + (non_operational_machines / total_machines) * 20 if total_machines > 0 else 2

        machine_details = "<br>".join([
            f"LmuId: {row['LmuId']}, State: {row['state']}, Linie: {row['Linie']}" +
            (f", Standplatz: {row['Standplatz']}" if pd.notna(row['Standplatz']) else "")
            for _, row in group.iterrows()
        ])

        color = 'operational'
        if non_operational_machines > 0:
            color = 'broken' if 'OUT_OF_ORDER' in group['state'].values else 'warning'

        return f"{machine_details}<br>", color, size, importance

    grouped = recent_stations.groupby('HstName').apply(aggregate_info).reset_index()
    grouped[['Machine_Info', 'Station_Status', 'Size', 'Service_Importance']] = pd.DataFrame(grouped[0].tolist(), index=grouped.index)
    grouped.drop(columns=[0], inplace=True)

    station_coordinates = recent_stations[['HstName', 'Latitude', 'Longitude']].drop_duplicates()
    grouped = pd.merge(grouped, station_coordinates, on='HstName', how='left')

    fig = px.scatter_mapbox(grouped,
                            lat="Latitude",
                            lon="Longitude",
                            color='Station_Status',
                            color_discrete_map=color_scale,
                            hover_name='HstName',
                            hover_data={
                                'Machine_Info': True,
                                'Service_Importance': ':.2f',  # Display Service Importance with 2 decimal places
                                'Size': False  # Exclude Size from hover data
                            },
                            size='Size',
                            size_max=30,
                            zoom=11,
                            mapbox_style="open-street-map")

    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)



def display(df):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    recent_stations = df.loc[df.groupby('Automatennr')['Timestamp'].idxmax()]
    create_aggregated_view(recent_stations)

    # Get the search query using the utility function
    search_query = search_utils.get_search_query(st)

    # Specify desired column order
    desired_order = ['Timestamp', 'state', 'LmuId', 'HstName', 'Standplatz', 'Linie',
                     'LmuState', 'AlarmState', 'CompType', 'CompNr', 'prevState',
                     'comment', 'Automatennr', 'EVU / Bereich', 'Status Gerät', 'Latitude', 'Longitude']

    # Column toggle
    available_columns = recent_stations.columns.tolist()
    selected_columns = st.multiselect("Select columns to display:", available_columns, default=desired_order)

    if not selected_columns:
        st.warning("Please select at least one column to display.")
        return

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

    # Check if any state filter is selected
    if not filtered_states:
        st.warning("Please select at least one state to display data.")
        return

    # Apply filters based on states
    filtered_df = recent_stations[recent_stations['state'].isin(filtered_states)]

    # Apply the search if there is a query
    if search_query:
        filtered_df = search_utils.perform_search(search_query, filtered_df)

    # Check if filtered dataframe is empty
    if not filtered_df.empty:
        # Apply selected columns to the DataFrame
        filtered_df = filtered_df[selected_columns]
        st.dataframe(filtered_df)
    else:
        # Display a message if no data matches the criteria
        st.warning("No data matches your criteria.")
