#!/usr/bin/env python3
"""Build data/centers.geojson for the map.

Merges two source families:
  1. Live facility-level points: OpenStreetMap (Overpass) + PeeringDB, US only.
  2. The researched hub list already in data/centers.geojson (source
     "research-2026") — kept as-is because it carries notes, power figures
     and photos.

Dedupes across everything within 1 km, preferring researched entries.

Usage: python3 scripts/fetch_data.py [--out data/centers.geojson]
"""
import argparse
import json
import math
import os
import urllib.parse
import urllib.request

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
PEERINGDB_URL = "https://peeringdb.com/api/fac?country=US"

OVERPASS_QUERY = """
[out:json][timeout:120];
area["ISO3166-1"="US"]->.us;
(
  nwr["telecom"="data_center"](area.us);
  nwr["building"="data_center"](area.us);
  nwr["man_made"="data_centre"](area.us);
);
out center tags;
"""


def fetch_json(url, data=None):
    if data is not None:
        req = urllib.request.Request(url, data=data.encode(), method="POST")
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.load(resp)


def haversine_km(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def from_osm():
    raw = fetch_json(OVERPASS_URL, data="data=" + urllib.parse.quote(OVERPASS_QUERY))
    feats = []
    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "name": tags.get("name") or tags.get("operator") or "Unnamed",
                "operator": tags.get("operator"),
                "city": tags.get("addr:city"),
                "state": tags.get("addr:state"),
                "type": "colo",
                "source": "osm",
            },
        })
    return feats


def from_peeringdb():
    raw = fetch_json(PEERINGDB_URL)
    feats = []
    for fac in raw.get("data", []):
        lat, lon = fac.get("latitude"), fac.get("longitude")
        if lat is None or lon is None:
            continue
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
            "properties": {
                "name": fac.get("name") or "Unnamed",
                "operator": fac.get("org"),
                "city": fac.get("city"),
                "state": fac.get("state"),
                "type": "colo",
                "source": "peeringdb",
            },
        })
    return feats


def load_researched(path):
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        fc = json.load(fh)
    return [f for f in fc.get("features", []) if str(f.get("properties", {}).get("source", "")).startswith("research")]


def dedupe(features, threshold_km=1.0):
    kept = []
    for f in features:  # researched entries come first, so they win ties
        c = f["geometry"]["coordinates"]
        if all(haversine_km((c[1], c[0]), (k["geometry"]["coordinates"][1], k["geometry"]["coordinates"][0])) > threshold_km for k in kept):
            kept.append(f)
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/centers.geojson")
    args = ap.parse_args()

    researched = load_researched(args.out)
    live = from_osm() + from_peeringdb()
    features = dedupe(researched + live)
    fc = {"type": "FeatureCollection", "features": features}
    with open(args.out, "w") as fh:
        json.dump(fc, fh)
    n_research = sum(1 for f in features if str(f["properties"].get("source", "")).startswith("research"))
    print(f"Wrote {len(features)} features to {args.out} ({n_research} researched, {len(features) - n_research} live)")


if __name__ == "__main__":
    main()
