# streets

POC for Hot Or Not for London Streets

## Data Acquisition

Boroughs publish lots of data sets including street bounds in geojson (and other gospatioal formats).

For Lambeth I, 

1. Went to [data portal](https://lambethopenmappingdata-lambethcouncil.opendata.arcgis.com/search)
2. Searched for "boundary", found [this dataset](https://lambethopenmappingdata-lambethcouncil.opendata.arcgis.com/maps/c42595fb230e41aba8f58805b73a11ec/explore)
3. On the map page go View Full Details > Layers > Borough Boundary > Download > Select `GeoJSON`
4. huzzah! 

With `lambeth_boundary.json` we leave the rest to python magic in `main.py`

