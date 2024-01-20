import pandas as pd


def calculate_downtime(df, start_state, end_state):
    """
    Calculate the duration of downtime based on state transitions.

    Args:
    df (pd.DataFrame): DataFrame containing machine data.
    start_state (str): The state indicating the start of downtime.
    end_state (str): The state indicating the end of downtime.

    Returns:
    pd.DataFrame: DataFrame with an additional 'Duration' column.
    """
    # Ensure 'Timestamp' is a datetime column
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])

    # Create a shifted column to find the end timestamp
    df['Next_Timestamp'] = df.groupby('LmuId')['Timestamp'].shift(-1)
    df['Next_State'] = df.groupby('LmuId')['state'].shift(-1)

    # Filter rows where the state changes from start_state to end_state
    filtered_df = df[(df['state'] == start_state) & (df['Next_State'] == end_state)]

    # Calculate duration
    filtered_df['Duration'] = filtered_df['Next_Timestamp'] - filtered_df['Timestamp']

    return filtered_df[['LmuId', 'Timestamp', 'Next_Timestamp', 'Duration']]
