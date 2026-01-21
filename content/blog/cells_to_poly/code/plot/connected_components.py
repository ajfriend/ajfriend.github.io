import util as u
import h3
import matplotlib.pyplot as plt
import random

def get_components(cells, edges_to_join):
    """Return a dict mapping each cell to its component root."""
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

    for edge in edges_to_join:
        origin, destination = h3.directed_edge_to_cells(edge)
        if origin in parent and destination in parent:
            union(origin, destination)

    return {cell: find(cell) for cell in cells}


def initial_colors(cells, seed):
    """Assign initial colors to individual cells using graph coloring."""
    random.seed(seed)

    # Build adjacency
    cell_set = set(cells)
    adj = {cell: [] for cell in cells}
    for cell in cells:
        for neighbor in h3.grid_disk(cell, 1):
            if neighbor != cell and neighbor in cell_set:
                adj[cell].append(neighbor)

    colors = plt.colormaps['tab20'].colors
    cell_colors = {}
    shuffled_colors = list(colors)
    shuffled_cells = list(cells)
    random.shuffle(shuffled_cells)

    for cell in shuffled_cells:
        neighbor_colors = {cell_colors.get(n) for n in adj[cell]}
        random.shuffle(shuffled_colors)
        for color in shuffled_colors:
            if color not in neighbor_colors:
                cell_colors[cell] = color
                break

    return cell_colors


def inherit_colors(cells, edges_to_join, prev_colors):
    """
    Assign colors based on component merging.
    Each merged component gets the color of its largest constituent group.
    """
    components = get_components(cells, edges_to_join)

    # Group cells by current component
    comp_to_cells = {}
    for cell, root in components.items():
        comp_to_cells.setdefault(root, []).append(cell)

    # For each component, count cells by their previous color
    component_colors = {}
    for root, comp_cells in comp_to_cells.items():
        color_counts = {}
        for cell in comp_cells:
            color = prev_colors[cell]
            color_counts[color] = color_counts.get(color, 0) + 1

        # Pick color with most cells
        best_color = max(color_counts.keys(), key=lambda c: color_counts[c])
        component_colors[root] = best_color

    return {cell: component_colors[components[cell]] for cell in cells}


def has_color_conflicts(cells, edges_to_join, cell_colors):
    """
    Check if any adjacent components have the same color.
    Adjacent components are those connected by edges NOT in edges_to_join.
    Returns list of conflicting edge pairs, or empty list if no conflicts.
    """
    components = get_components(cells, edges_to_join)

    # Get all edges and remove the joined ones
    all_edges = u.cells_to_edges(cells)
    edges_to_remove = u.twinning(*edges_to_join)
    boundary_edges = all_edges - edges_to_remove

    # Check edges that still exist (boundary edges) for same-color components
    conflicts = []
    seen = set()

    for edge in boundary_edges:
        origin, dest = h3.directed_edge_to_cells(edge)
        if origin not in components or dest not in components:
            continue

        # Only check if they're in different components
        if components[origin] != components[dest]:
            pair = tuple(sorted([origin, dest]))
            if pair not in seen:
                seen.add(pair)
                if cell_colors[origin] == cell_colors[dest]:
                    conflicts.append(pair)

    return conflicts


def generate_color_stages(cells, all_pairs, stage_cuts, seed):
    """
    Generate colors for all stages. Returns list of color dicts, one per stage.
    stage_cuts: list of indices into all_pairs for each stage, e.g. [0, 16, 35, len(all_pairs)]
    """
    colors_0 = initial_colors(cells, seed=seed)
    stages = [colors_0]

    prev_colors = colors_0
    for cut in stage_cuts[1:]:
        next_colors = inherit_colors(cells, all_pairs[:cut], prev_colors)
        stages.append(next_colors)
        prev_colors = next_colors

    return stages


def find_valid_coloring(cells, all_pairs, stage_cuts, overall_seed, max_iters=1000):
    """
    Stochastically search for a coloring with no conflicts at any stage.
    Returns list of color dicts, one per stage.
    """
    random.seed(overall_seed)

    for i in range(max_iters):
        seed = random.randint(0, 2**32 - 1)
        stages = generate_color_stages(cells, all_pairs, stage_cuts, seed)

        # Check for conflicts at each stage
        has_conflict = False
        for stage_idx, colors in enumerate(stages):
            edges_to_join = all_pairs[:stage_cuts[stage_idx]]
            conflicts = has_color_conflicts(cells, edges_to_join, colors)
            if conflicts:
                print(f"  iter {i}: seed {seed}, stage {stage_idx} has {len(conflicts)} conflict(s)")
                has_conflict = True
                break

        if not has_conflict:
            print(f"Found valid coloring at iter {i} with seed {seed}")
            return stages

    print(f"No valid coloring found after {max_iters} iterations")
    return stages  # Return last attempt


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



# --- Plotting ---

def make_plot(filename, cells, edges_to_join, cell_colors):
    """
    Generate a plot showing cell edges after removing symmetric pairs.

    Args:
        filename: Output SVG filename
        cells: List of H3 cell indices
        edges_to_join: List of edges whose symmetric pairs should be removed
        cell_colors: Dict mapping cell -> color (or None for no fill)
    """
    all_edges = u.cells_to_edges(cells)
    edges_to_remove = u.twinning(*edges_to_join)
    remaining_edges = all_edges - edges_to_remove

    plot_figure(filename, remaining_edges, cell_colors)


all_edges = u.cells_to_edges(cells)
all_pairs = sorted([t[0] for t in u.get_pair_tuples(all_edges)])
random.seed(47)
random.shuffle(all_pairs)

# Stage cuts: indices into all_pairs for each stage
stage_cuts = [0, 16, 35, len(all_pairs)]

# Find a valid coloring with no conflicts at any stage
overall_seed = 123
stages = find_valid_coloring(cells, all_pairs, stage_cuts, overall_seed)

# Boundary edges only, no background colors
no_colors = {cell: None for cell in cells}
make_plot('figs/conn_comp_white.svg', cells, all_pairs, no_colors)

# Plot each stage
for i, (cut, colors) in enumerate(zip(stage_cuts, stages)):
    make_plot(f'figs/conn_comp_colors_{i}.svg', cells, all_pairs[:cut], colors)


