"""
This program expects a lambeth_boundary.json file.

It will use the boundary file to sample coordinates on the streets that it finds.

It will give back three datasates:
1. GeoJSON of generated street coordinates
2. Metadata for the coordinates
3. plain JSON dataset of both that can be used to drive a rudimentary webapp.
"""
import geopandas as gpd
import osmnx as ox
import numpy as np
from shapely.geometry import Point, LineString
import pandas as pd

# Load Lambeth boundary
lambeth = gpd.read_file('lambeth_boundary.geojson')
lambeth_polygon = lambeth.geometry.iloc[0]

# Download street network within Lambeth
G = ox.graph_from_polygon(lambeth_polygon, network_type='drive')

# Convert graph to GeoDataFrame
gdf_streets = ox.graph_to_gdfs(G, nodes=False, edges=True)

def generate_points_along_line(line, num_points):
    distances = np.linspace(0, line.length, num_points)
    return [line.interpolate(distance) for distance in distances]

all_points = []
point_metadata = []
point_id = 0

for idx, street in gdf_streets.iterrows():
    # Generate points along the street
    num_points = max(2, int(street.geometry.length / 50))  # One point every 50 meters, minimum 2 points
    street_points = generate_points_along_line(street.geometry, num_points)
    
    # Filter points to ensure they're within Lambeth
    valid_points = [point for point in street_points if lambeth_polygon.contains(point)]
    
    for point in valid_points:
        all_points.append({'id': point_id, 'geometry': point})
        point_metadata.append({
            'id': point_id,
            'street_id': idx[0],  # Assuming the index is a tuple (u, v, key)
            'street_name': street.get('name', 'Unnamed'),
            'highway_type': street.get('highway', 'Unknown'),
            'oneway': street.get('oneway', False),
            'maxspeed': street.get('maxspeed', None),
            # Add any other metadata you want to preserve
        })
        point_id += 1

# Convert to GeoDataFrame for easy export
gdf_points = gpd.GeoDataFrame(all_points, crs=gdf_streets.crs)
df_metadata = pd.DataFrame(point_metadata)

# Export to GeoJSON and CSV
gdf_points.to_file("lambeth_street_points.geojson", driver="GeoJSON")
df_metadata.to_csv("lambeth_street_points_metadata.csv", index=False)

print(f"Generated {len(all_points)} points on streets in Lambeth")
print("Exported point data to 'lambeth_street_points.geojson'")
print("Exported metadata to 'lambeth_street_points_metadata.csv'")

# Load the GeoJSON file with point coordinates
gdf = gpd.read_file('lambeth_street_points.geojson')

# Load the CSV file with metadata
metadata = {}
with open('lambeth_street_points_metadata.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        metadata[int(row['id'])] = row

# Combine the data
combined_data = []
for _, point in gdf.iterrows():
    point_id = point['id']
    point_data = {
        'id': point_id,
        'lat': point.geometry.y,
        'lng': point.geometry.x,
        **metadata[point_id]  # Unpack all metadata for this point
    }
    combined_data.append(point_data)

# Save the combined data to a JSON file
with open('lambeth_combined_street_data.json', 'w') as json_file:
    json.dump(combined_data, json_file, indent=2)

print(f"Combined data saved to 'lambeth_combined_street_data.json'")
print(f"Total points: {len(combined_data)}")
