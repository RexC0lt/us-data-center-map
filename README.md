# US Data Center Map

Interactive map of data center locations across the United States.

## Run it

Any static file server works:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Or enable GitHub Pages (Settings → Pages → Deploy from branch → `/root`).

## Data

`data/centers.geojson` holds 100+ US data center locations researched in 2026
(CBRE / Avison Young market reports, operator announcements), each tagged with
type (hyperscale / colocation / mixed), operators, and market notes. Seven
hyperscale campuses also have a photo (via Wikimedia Commons `image_file`),
shown in the map popup when available. It can be regenerated/expanded from
live sources with:

```bash
pip install requests
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
