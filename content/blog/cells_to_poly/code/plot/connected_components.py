import util as u
import h3
import matplotlib.pyplot as plt
import random
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

# Graph coloring for cell outlines
colors = plt.cm.get_cmap('tab20').colors
adj = {cell: [] for cell in cells}
cell_set = set(cells)
for cell in cells:
    # Use h3.grid_disk to find neighbors
    neighbors = h3.grid_disk(cell, 1)
    for neighbor in neighbors:
        if neighbor != cell and neighbor in cell_set:
            adj[cell].append(neighbor)

cell_colors = {}
# Make a mutable copy of the colors list to shuffle
shuffled_colors = list(colors)
for cell in cells:
    neighbor_colors = {cell_colors.get(neighbor) for neighbor in adj[cell]}

    random.shuffle(shuffled_colors)

    for color in shuffled_colors:
        if color not in neighbor_colors:
            cell_colors[cell] = color
            break

with u.svg('figs/conn_comp.svg', size=8) as ax:
    # Fill cell interiors
    for cell, color in cell_colors.items():
        u.fill_cell(ax, cell, color=color, alpha=0.5, theta=1.0)

    # Plot edges on top
    edges1 = edges - u.twinning(
        # '1198f50703c3ffff',
        # '1198f50703cbffff',
    )
    u.plot_edges(edges1, ax=ax, arrow_scale=12, theta=0.8)

