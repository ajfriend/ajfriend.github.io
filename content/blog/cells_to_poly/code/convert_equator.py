"""Convert equator.json to GeoJSON FeatureCollection format."""
import json

# Read source file
with open('/Users/aj/work/ajfriend.github.io/data/globe_coords/equator.json') as f:
    data = json.load(f)

# Wrap in GeoJSON FeatureCollection
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "fill": "#dc3545",
                "fillOpacity": 0.3,
                "stroke": "#dc3545",
                "strokeWidth": 2
            },
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": data["coordinates"]
            }
        }
    ]
}

# Write to destination
with open('/Users/aj/work/ajfriend.github.io/content/blog/cells_to_poly/data/equator.json', 'w') as f:
    json.dump(geojson, f, indent=2)

print("Created data/equator.json")
