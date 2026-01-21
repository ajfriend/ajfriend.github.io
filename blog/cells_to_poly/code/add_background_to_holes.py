"""Add intro_poly multipolygon as grey dashed background to holes_*.json files."""
import json

# Read the intro_poly.json to get the multipolygon
with open('/Users/aj/work/ajfriend.github.io/content/blog/cells_to_poly/data/intro_poly.json') as f:
    intro_data = json.load(f)

# Extract just the first polygon from the multipolygon
first_polygon_coords = intro_data["features"][0]["geometry"]["coordinates"][0]

# Background feature with light grey, dashed stroke
background_feature = {
    "type": "Feature",
    "properties": {
        "fill": "none",
        "stroke": "#999999",
        "strokeWidth": 1,
        "strokeDasharray": "4 2"
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": first_polygon_coords
    }
}

# Update each holes_*.json file
for i in range(4):
    filepath = f'/Users/aj/work/ajfriend.github.io/content/blog/cells_to_poly/data/holes_{i}.json'

    with open(filepath) as f:
        data = json.load(f)

    # Replace the first feature (background) with the corrected one
    data["features"][0] = background_feature

    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Updated {filepath}")

print("Done!")
