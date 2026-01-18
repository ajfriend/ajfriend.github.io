import matplotlib.pyplot as plt
import h3
import numpy as np
from contextlib import contextmanager

# Make SVG output deterministic (no random IDs or timestamps)
plt.rcParams['svg.hashsalt'] = 'h3-cells-to-poly'

@contextmanager
def svg(filename, show_axis=False, size=5):
    """Context manager for creating and saving SVG figures.

    Usage:
        with svg('figs/my_figure.svg') as ax:
            plot_edges(edges, ax=ax)
    """
    fig, ax = plt.subplots(figsize=(size, size))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_aspect('equal')
    if not show_axis:
        ax.axis('off')
    yield ax
    save_svg(fig, filename)
    plt.close(fig)

def figure(size=5):
    fig, ax = plt.subplots(figsize=(size, size))

    # ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    return fig, ax

def directed_line(ax, latlng1, latlng2, label=None, linewidth=1.5, arrow_scale=22, color='black', arrow_alpha=0.4):
    (y1, x1) = latlng1
    (y2, x2) = latlng2

    ax.plot(
        [x1, x2],
        [y1, y2],
        color=color,
        linewidth=linewidth,
    )

    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2

    dx = x2 - x1
    dy = y2 - y1
    length = (dx**2 + dy**2)**0.5
    if length == 0:
        return
    dx /= length
    dy /= length

    # arrowhead centered on midpoint
    offset = 0.02 * length  # 2% of segment length
    ax.annotate(
        '',
        xy = (
            mx + dx * offset,
            my + dy * offset,
        ),
        xytext = (
            mx - dx * offset,
            my - dy * offset,
        ),
        arrowprops = dict(
            arrowstyle = '->',
            color = color,
            lw = linewidth,
            mutation_scale = arrow_scale,
            alpha = arrow_alpha,
        )
    )

    # label (offset perpendicular to the line, towards cell center)
    if label is not None:
        # perpendicular direction
        px = -dy
        py = dx
        text_offset = 0.16 * length
        ax.text(
            mx + px * text_offset,
            my + py * text_offset,
            str(label),
            ha='center',
            va='center',
            fontsize=10,
            color='black',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1),
        )

def plot_edge(ax, e):
    line = h3.directed_edge_to_boundary(e)
    line = line[0], line[-1]
    directed_line(ax, *line)


def scale_edge(e, theta=1):
    p1 = h3.cell_to_latlng(h3.get_directed_edge_origin(e))

    bd = h3.directed_edge_to_boundary(e)
    p2, p3 = bd[0], bd[-1]

    p1 = np.array(p1)
    p2 = np.array(p2)
    p3 = np.array(p3)

    p2 = p1 + theta*(p2 - p1)
    p3 = p1 + theta*(p3 - p1)

    p2 = list(p2)
    p3 = list(p3)

    return p2, p3

PASTEL_COLORS = {
    'pink': '#FFB6C1',
    'blue': '#ADD8E6',
    'green': '#98FB98',
    'yellow': '#FFFACD',
    'lavender': '#E6E6FA',
    'peach': '#FFDAB9',
    'mint': '#BDFCC9',
    'coral': '#FFB5A7',
}

def fill_cell(ax, cell, color='blue', alpha=0.5, theta=0.9):
    """Fill the interior of a hex cell with a pastel color.

    color: key from PASTEL_COLORS or any matplotlib color
    """
    if color in PASTEL_COLORS:
        color = PASTEL_COLORS[color]

    center = np.array(h3.cell_to_latlng(cell))
    boundary = h3.cell_to_boundary(cell)

    # Scale boundary points towards center (same as edge scaling)
    scaled = []
    for pt in boundary:
        pt = np.array(pt)
        scaled_pt = center + theta * (pt - center)
        scaled.append(scaled_pt)

    # Convert to x, y coordinates for plotting
    ys = [p[0] for p in scaled]
    xs = [p[1] for p in scaled]

    ax.fill(xs, ys, color=color, alpha=alpha, edgecolor='none', linewidth=0)


def reverse_edge(e):
    return h3.cells_to_directed_edge(*h3.directed_edge_to_cells(e)[::-1])


def fill_gap(ax, edge, color='blue', alpha=0.5, theta=0.9):
    """Fill the gap between two adjacent cells.

    edge: one of the directed edges between the two cells
    color: key from PASTEL_COLORS or any matplotlib color
    """
    if color in PASTEL_COLORS:
        color = PASTEL_COLORS[color]

    # Get scaled edge points from both sides
    p1, p2 = scale_edge(edge, theta=theta)
    p3, p4 = scale_edge(reverse_edge(edge), theta=theta)

    # Form quadrilateral: p1 -> p2 -> p3 -> p4
    xs = [p1[1], p2[1], p3[1], p4[1]]
    ys = [p1[0], p2[0], p3[0], p4[0]]

    ax.fill(xs, ys, color=color, alpha=alpha, edgecolor='none', linewidth=0)

def reverse_set(edges):
    return set(
        reverse_edge(e)
        for e in edges
    )


def plot_edges(edges, ax=None):
    if ax is None:
        fig, ax = figure(5)
    else:
        fig = ax.get_figure()

    for e in sorted(edges):
        p1, p2 = scale_edge(e, theta=0.9)
        directed_line(ax, p1, p2)

    return fig


def cells_to_edges(cells):
    edges = set(
        e
        for c in cells
        for e in h3.origin_to_directed_edges(c)
    )
    return edges

def get_pair_tuples(edges):
    pairs = set(
        tuple(sorted([e, reverse_edge(e)]))
        for e in (edges & reverse_set(edges))
    )
    return pairs

def twinning(*edges):
    "For a set of edges, return the set of those edges, along with their opposites"
    edges = set(edges)
    rev = {reverse_edge(e) for e in edges}
    return edges | rev

def save_svg(fig, path):
    """Save figure as SVG with deterministic output (no date/creator metadata)."""
    fig.savefig(path, bbox_inches='tight', metadata={'Date': None, 'Creator': None})
