# US Data Center Map

Interactive map of data center locations across the United States.

## Run it

Any static file server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Or enable GitHub Pages (Settings -> Pages -> Deploy from branch -> /root).

## Data

`data/centers.geojson` is the dataset the map renders. It starts as a seed of
major US data center hubs and can be regenerated/expanded with:

```bash
python3 scripts/fetch_data.py
```

The pipeline pulls facilities tagged `telecom=data_center` /
`building=data_center` in the US from OpenStreetMap (Overpass API) plus all
US facilities from PeeringDB, dedupes points within 1 km, and writes the
GeoJSON file.

## Structure

```
├── index.html            # Leaflet map with clustering + source filters
├── data/centers.geojson  # map dataset
└── scripts/fetch_data.py # data pipeline (OSM + PeeringDB)
```
