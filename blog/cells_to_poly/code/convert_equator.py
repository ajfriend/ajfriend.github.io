"""Convert equator.json to GeoJSON FeatureCollection with LineStrings for each ring."""
import json

# Read source file
with open('/Users/aj/work/ajfriend.github.io/data/globe_coords/equator.json') as f:
    data = json.load(f)

# Colors for different rings
colors = ['#9b59b6', '#e67e22']  # purple and orange

# Extract rings from the MultiPolygon and convert to LineStrings
features = []
ring_index = 0

for polygon in data["coordinates"]:
    for ring in polygon:
        color = colors[ring_index % len(colors)]
        features.append({
            "type": "Feature",
            "properties": {
                "stroke": color,
                "strokeWidth": 2,
                "arrowStep": 3
            },
            "geometry": {
                "type": "LineString",
                "coordinates": ring
            }
        })
        ring_index += 1

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Write to destination
with open('/Users/aj/work/ajfriend.github.io/content/blog/cells_to_poly/data/equator.json', 'w') as f:
    json.dump(geojson, f, indent=2)

print(f"Created data/equator.json with {ring_index} rings")
