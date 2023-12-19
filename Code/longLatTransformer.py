import pandas as pd
import os
from shapely.wkt import loads
from pyproj import Transformer
from shapely.geometry import MultiPolygon

# Function to extract centroid coordinates from MULTIPOLYGON
def extract_centroid_coords(multi_polygon_str):
    try:
        multi_polygon = loads(multi_polygon_str)
        if isinstance(multi_polygon, MultiPolygon):
            centroid = multi_polygon.centroid
            return centroid.x, centroid.y
        return None, None
    except Exception as e:
        print(f"Error in extracting centroid: {e}")
        return None, None

# Function to transform coordinates using Transformer class
def transform_coords(x, y):
    if x is None or y is None:
        return None, None
    transformer = Transformer.from_crs("epsg:25832", "epsg:4326", always_xy=True)
    try:
        lon, lat = transformer.transform(x, y)
        return lat, lon  # Switched latitude and longitude here
    except Exception as e:
        print(f"Error in transforming coordinates: {e}")
        return None, None

# List all CSV files ending with '_EPSG_25832.csv'
folder_path = '/Users/timmdill/Downloads/Geodaten Hamburg'
csv_files = [f for f in os.listdir(folder_path) if f.endswith('_EPSG_25832.csv')]

# Read and store each CSV file in a list
data_frames = []
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    df = pd.read_csv(file_path)
    # Extract centroid coordinates and transform
    df['x'], df['y'] = zip(*df['{https://registry.gdi-de.org/id/de.hh.up}geom'].apply(extract_centroid_coords))
    df['latitude'], df['longitude'] = zip(*df.apply(lambda row: transform_coords(row['x'], row['y']), axis=1))
    data_frames.append(df)

# Concatenate all DataFrames into one
appended_data = pd.concat(data_frames, ignore_index=True)

# Save the combined data
appended_data.to_csv('/Users/timmdill/Downloads/Geodaten Hamburg/combined_data.csv', index=False)
