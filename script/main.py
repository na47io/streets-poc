import geopandas as gpd
import osmnx as ox
import numpy as np
from shapely.geometry import Point, LineString
import pandas as pd

# Load Lambeth boundary (see README on where to get this)
lambeth = gpd.read_file('lambeth_boundary.geojson')
lambeth_polygon = lambeth.geometry.iloc[0]

# Download street network within Lambeth
G = ox.graph_from_polygon(lambeth_polygon, network_type='drive')

# Convert graph to GeoDataFrame
gdf_streets = ox.graph_to_gdfs(G, nodes=False, edges=True)

all_streets = gdf_streets[(gdf_streets.highway=="residential")&(gdf_streets.name!="")].reset_index()
all_streets.name = all_streets.name.astype(str)

names = all_streets.name.unique()

rows = []

for i,name in enumerate(names):
  subgdf = all_streets[all_streets.name==name]
  points, street_len = get_points(subgdf)
  row = {
      'name': name, 
      'geometry': unary_union(points),
      'points_on_street': len(points),
      'street_id': i,
      'highway': subgdf.highway.iloc[0],
      'oneway': subgdf.oneway.iloc[0],
      'maxspeed': subgdf.maxspeed.iloc[0],
      'length': street_len
      }
  rows.append(row)

gdf = gpd.GeoDataFrame(rows, crs=all_streets.crs)

# wirte it all down before i forget
final = gdf.explode(ignore_index=True)
final['lng'] = final.geometry.x
final['lat'] = final.geometry.y

final.to_file("lambeth_points.geojson", driver="GeoJSON")

# save rows as regular json
df = final.drop(columns=['geometry'])
df.to_json("lambeth_points.json", orient='records')rint(f"Total points: {len(combined_data)}")
