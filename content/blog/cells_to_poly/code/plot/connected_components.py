import util as u
import h3
import matplotlib.pyplot as plt
import random
import pprint
random.seed(42)

cells = [
    '8966dbda96bffff',
    '8966dbda947ffff',
    '8966dbda94fffff',
    '8966dbdabb3ffff',
    '8966dbdaba3ffff',
    '8966dbdabafffff',
    '8966dbc36dbffff',
    '8966dbc36c3ffff',
    '8966dbc36d7ffff',
    '8966dbc369bffff',
    '8966dbda967ffff',
    '8966dbda977ffff',
    '8966dbda973ffff',
    '8966dbdababffff',
    '8966dbdab17ffff',
    '8966dbdab13ffff',
    '8966dbdabc7ffff',
    '8966dbdabd7ffff',
    '8966dbdab9bffff',
    '8966dbdab93ffff',
    '8966dbda82fffff',
    '8966dbda827ffff',
    '8966dbda953ffff',
    '8966dbda957ffff',
    '8966dbda943ffff',
    '8966dbda94bffff',
    '8966dbdab97ffff',
    '8966dbdabbbffff',
    '8966dbdab87ffff',
    '8966dbda903ffff',
    '8966dbda907ffff',
]

edges = u.cells_to_edges(cells)



# List of edges to "join". When an edge is in this list, the two cells
# on either side of it are considered "joined" and will share the same
# background color. The edge and its reverse will be removed from the plot.
#
# You can get edge IDs by creating them from adjacent cells, e.g.:
# h3.cells_to_directed_edge('8966dbda96bffff', '8966dbda96fffff')
#
# You can find adjacent cells by running this script and looking at the
# printed "pair_tuples" output.

edges_to_join = [
    '11966dbc36dbffff',
    '11966dbda827ffff',
    '11966dbda903ffff',
    '11966dbda943ffff',
    '11966dbda947ffff',
    '13966dbdabd7ffff',
    '13966dbda82fffff',
    '13966dbdab87ffff',
    '11966dbda903ffff',
    '11966dbdab97ffff',
    '12966dbc36d7ffff',
    '12966dbdabbbffff',
    '11966dbdab93ffff',
    '12966dbda943ffff',
    '11966dbda973ffff',
    '13966dbdabbbffff',
]

# DSU data structure to track joined components
parent = {cell: cell for cell in cells}
def find(cell):
    if parent[cell] == cell:
        return cell
    parent[cell] = find(parent[cell])
    return parent[cell]

def union(cell1, cell2):
    root1 = find(cell1)
    root2 = find(cell2)
    if root1 != root2:
        parent[root2] = root1

# Join components based on edges_to_join
for edge in edges_to_join:
    origin, destination = h3.directed_edge_to_cells(edge)
    if origin in parent and destination in parent:
        union(origin, destination)

# Adjacency graph for coloring
adj = {cell: [] for cell in cells}
cell_set = set(cells)
for cell in cells:
    neighbors = h3.grid_disk(cell, 1)
    for neighbor in neighbors:
        if neighbor != cell and neighbor in cell_set:
            adj[cell].append(neighbor)

# Modified graph coloring for components
colors = plt.cm.get_cmap('tab20').colors
component_colors = {}
shuffled_colors = list(colors)
shuffled_cells = list(cells)
random.shuffle(shuffled_cells)

for cell in shuffled_cells:
    root = find(cell)
    if root in component_colors:
        continue

    # Find colors of neighboring components
    neighbor_component_colors = set()
    component_cells = [c for c in cells if find(c) == root]
    for c in component_cells:
        for neighbor in adj[c]:
            neighbor_root = find(neighbor)
            if neighbor_root != root and neighbor_root in component_colors:
                neighbor_component_colors.add(component_colors[neighbor_root])

    random.shuffle(shuffled_colors)
    for color in shuffled_colors:
        if color not in neighbor_component_colors:
            component_colors[root] = color
            break

# Assign colors to cells based on their component's color
cell_colors = {cell: component_colors.get(find(cell)) for cell in cells}


with u.svg('figs/conn_comp.svg', size=8) as ax:
    # Fill cell interiors
    for cell, color in cell_colors.items():
        if color: # Color might be None if coloring fails
            u.fill_cell(ax, cell, color=color, alpha=0.5, theta=1.0)

    # Plot edges on top, removing the joined edges
    edges_to_remove = u.twinning(*edges_to_join)
    edges_to_plot = edges - edges_to_remove
    # Print remaining pair tuples (eligible for removal)
    remaining_pair_tuples = u.get_pair_tuples(edges_to_plot)
    remaining_pair_tuples = [
        a
        for (a,b) in remaining_pair_tuples
    ]

    print("\nRemaining pair tuples (eligible for removal):")
    pprint.pprint(remaining_pair_tuples)

    u.plot_edges(edges_to_plot, ax=ax, arrow_scale=12, theta=0.8)
