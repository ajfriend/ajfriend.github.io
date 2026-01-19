import h3
import util as u

cells = ['898f50703cbffff', '898f50703cfffff']
edges = u.cells_to_edges(cells)

# Find the canceling pair
pairs = u.get_pair_tuples(edges)
a, b = list(pairs)[0]  # a and b are reverses of each other

# Get edges in counter-clockwise order for each cell
# Index arrays from the C code
idxh = [0, 4, 3, 5, 1, 2]

def edges_ccw(cell):
    """Get directed edges in counter-clockwise order."""
    raw = h3.origin_to_directed_edges(cell)
    return [raw[i] for i in idxh]

def get_neighbors(edge, cell):
    """Return (prev, next) edges in counter-clockwise order."""
    ccw = edges_ccw(cell)
    idx = ccw.index(edge)
    prev_edge = ccw[(idx - 1) % len(ccw)]
    next_edge = ccw[(idx + 1) % len(ccw)]
    return prev_edge, next_edge

cell_a = h3.get_directed_edge_origin(a)
cell_b = h3.get_directed_edge_origin(b)

a_prev, a_next = get_neighbors(a, cell_a)
b_prev, b_next = get_neighbors(b, cell_b)

labels = {
    a: 'a',
    b: 'b',
    a_prev: 'a⁻',
    a_next: 'a⁺',
    b_prev: 'b⁻',
    b_next: 'b⁺',
}

with u.svg('figs/two_cells_before_labels.svg') as ax:
    for e in sorted(edges):
        p1, p2 = u.scale_edge(e, theta=0.9)
        label = labels.get(e)
        u.directed_line(ax, p1, p2, label=label)

with u.svg('figs/two_cells_after_labels.svg') as ax:
    edges_after = edges - {a, b}
    for e in sorted(edges_after):
        p1, p2 = u.scale_edge(e, theta=0.9)
        label = labels.get(e)
        u.directed_line(ax, p1, p2, label=label)
