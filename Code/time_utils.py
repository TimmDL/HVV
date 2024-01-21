import pandas as pd

def calculate_transition_durations(df, start_date, end_date):
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df[(df['Timestamp'].dt.date >= start_date) & (df['Timestamp'].dt.date <= end_date)]

    operational_states = ['OPERATIONAL', 'IN_OPERATION']
    transitions_data = {
        'operational_to_warning': [],
        'warning_to_out_of_order': [],
        'out_of_order_to_operational': [],
        'operational_to_out_of_order': []
    }

    for lmu_id, group in df.groupby('LmuId'):
        group = group.sort_values(by='Timestamp')

        last_operational_timestamp = None
        first_warning_timestamp = None
        last_out_of_order_timestamp = None
        first_out_of_order_timestamp = None

        for _, row in group.iterrows():
            if row['state'] in operational_states:
                last_operational_timestamp = row['Timestamp']
            elif row['state'] == 'WARNING' and first_warning_timestamp is None:
                first_warning_timestamp = row['Timestamp']
                if last_operational_timestamp is not None:
                    duration = (first_warning_timestamp - last_operational_timestamp).total_seconds() / 3600
                    transitions_data['operational_to_warning'].append(duration)
            elif row['state'] == 'OUT_OF_ORDER':
                if first_out_of_order_timestamp is None:
                    first_out_of_order_timestamp = row['Timestamp']
                    if last_operational_timestamp is not None:
                        duration = (first_out_of_order_timestamp - last_operational_timestamp).total_seconds() / 3600
                        transitions_data['operational_to_out_of_order'].append(duration)
                last_out_of_order_timestamp = row['Timestamp']
                if first_warning_timestamp is not None:
                    duration = (last_out_of_order_timestamp - first_warning_timestamp).total_seconds() / 3600
                    transitions_data['warning_to_out_of_order'].append(duration)
            elif row['state'] in operational_states and last_out_of_order_timestamp is not None:
                operational_timestamp = row['Timestamp']
                duration = (operational_timestamp - last_out_of_order_timestamp).total_seconds() / 3600
                transitions_data['out_of_order_to_operational'].append(duration)
                break  # Break after first transition to operational state

    avg_durations = {key: round(pd.Series(data).mean(), 2) for key, data in transitions_data.items() if data}

    return avg_durations