import pandas as pd
import re

column_names = ['EVU/Bereich', 'Automatennr', 'StatusGerät','HstName','Standplatz','Line']
df = pd.read_excel('Data/ssts_Haltestellen.xlsx', header=None, names=column_names, engine='openpyxl')

# Drop rows where all elements are NaN
df.dropna(how='all', inplace=True)

# Define regular expressions
regex_patterns = [
    'U1',
    'U2',
    'U3',
    'U4',
    'BUS',
    'HADAG',
    # Add more patterns here
]

# Initialize a variable to hold the last found match
last_match = 'unknown'

# Function to search for regex patterns in a given text
def search_patterns(text):
    global last_match
    for pattern in regex_patterns:
        if pd.isna(text):
            continue
        match = re.search(pattern, text)
        if match:
            last_match = match.group()
            return last_match
    return last_match

# Apply the function to each row in a specific column
df['col6'] = df['col1'].apply(search_patterns)

# Save the modified DataFrame to a new CSV file
df.to_excel('Data/clean.csv', index=False)
