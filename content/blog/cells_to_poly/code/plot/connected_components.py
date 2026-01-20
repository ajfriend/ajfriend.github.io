import util as u
import h3
import matplotlib.pyplot as plt
import random
import pprint

def color_cells(cells, edges_to_join, seed):
    """
    Assigns colors to cells based on a graph coloring algorithm,
    joining components specified by edges_to_join.
    A random seed is used to ensure reproducible colorings.
    """
    random.seed(seed)

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
    colors = plt.colormaps['tab20'].colors
    component_colors = {}
    shuffled_colors = list(colors)
    shuffled_cells = list(cells)
    random.shuffle(shuffled_cells)

    for cell in shuffled_cells:
        root = find(cell)
        if root in component_colors:
            continue

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
    
    return {cell: component_colors.get(find(cell)) for cell in cells}

def color_components(cells):
    """
    Assigns a single color to each connected component of cells.
    """
    parent = {cell: cell for cell in cells}
    cell_set = set(cells)
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

    for cell in cells:
        neighbors = h3.grid_disk(cell, 1)
        for neighbor in neighbors:
            if neighbor != cell and neighbor in cell_set:
                union(cell, neighbor)

    colors = plt.colormaps['tab20'].colors
    component_colors = {}
    i = 0
    for cell in cells:
        root = find(cell)
        if root not in component_colors:
            component_colors[root] = colors[i]
            i = (i + 1) % len(colors)
    
    return {cell: component_colors[find(cell)] for cell in cells}


def plot_figure(filename, edges_to_plot, cell_colors, size=8, arrow_scale=12, theta=0.8):
    """Helper function to generate a single plot."""
    with u.svg(filename, size=size) as ax:
        for cell, color in cell_colors.items():
            if color:
                u.fill_cell(ax, cell, color=color, alpha=0.5, theta=1.0)
        
        u.plot_edges(edges_to_plot, ax=ax, arrow_scale=arrow_scale, theta=theta)

# --- Main script ---

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

# List of edges to "join".
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

# --- Plotting ---

def make_plot(filename, cells, edges_to_join=[], seed=42, show_colors=True):
    """
    Generate a plot showing cell edges after removing symmetric pairs.

    Args:
        filename: Output SVG filename
        cells: List of H3 cell indices
        edges_to_join: List of edges whose symmetric pairs should be removed
        seed: Random seed for color assignment
        show_colors: Whether to show background cell colors
    """
    all_edges = u.cells_to_edges(cells)
    edges_to_remove = u.twinning(*edges_to_join)
    remaining_edges = all_edges - edges_to_remove

    if show_colors:
        cell_colors = color_cells(cells, edges_to_join, seed)
    else:
        cell_colors = {cell: None for cell in cells}

    plot_figure(filename, remaining_edges, cell_colors)

    # Print removable edges
    remaining_pairs = u.get_pair_tuples(remaining_edges)
    print(f"\n{filename}")
    if remaining_pairs:
        pprint.pprint(sorted([t[0] for t in remaining_pairs]))
    else:
        print("  (no remaining pairs)")


all_edges = u.cells_to_edges(cells)
all_pairs = [t[0] for t in u.get_pair_tuples(all_edges)]
# TODO: shuffle all_pairs (with a random key)

# Boundary edges only, no background colors
make_plot('figs/conn_comp_boundary_only.svg', cells, edges_to_join=all_pairs, seed=42, show_colors=False)

# All edges, with background colors
make_plot('figs/conn_comp_all.svg', cells, edges_to_join=[], seed=42, show_colors=True)

# Partial join, with background colors
# TODO: replace edges_to_join with the first few `all_pairs`, same number of edges
make_plot('figs/conn_comp_joined.svg', cells, edges_to_join=edges_to_join, seed=44, show_colors=True)

# Boundary edges only, with background colors
make_plot('figs/conn_comp_boundary.svg', cells, edges_to_join=all_pairs, seed=42, show_colors=True)


