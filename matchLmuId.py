import pandas as pd
import re

# Load your CSV file
df = pd.read_csv('/Users/timmdill/Downloads/auditlog-all.csv')

# Define a function to extract the number
def extract_number(s):
    match = re.search(r'-(\d+)-', s)
    return match.group(1) if match else None

# Apply the function to the 'LmuId' column and create a new column 'col2'
df['Automatennr'] = df['LmuId'].apply(extract_number)

# Save the modified DataFrame to a new CSV file
df.to_csv('/Users/timmdill/Downloads/matched-auditlog-all.csv', index=False)
