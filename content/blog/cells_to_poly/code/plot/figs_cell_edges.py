import h3
import util as u

cells = ['898f50703cbffff', '898f50703cfffff']

# Find edges that have their reverse in the set (the shared edge)
all_edges = u.cells_to_edges(cells)
paired_edges = all_edges & u.reverse_set(all_edges)

def plot_cell_outline(ax, cell, color='darkblue', linewidth=2):
    """Plot the full outline of a cell."""
    boundary = h3.cell_to_boundary(cell)
    xs = [p[1] for p in boundary] + [boundary[0][1]]
    ys = [p[0] for p in boundary] + [boundary[0][0]]
    ax.plot(xs, ys, color=color, linewidth=linewidth)

with u.svg('figs/two_cells_edges.svg') as ax:
    for cell in cells:
        plot_cell_outline(ax, cell)
        for edge in h3.origin_to_directed_edges(cell):
            p1, p2 = u.scale_edge(edge, theta=0.8)
            color = 'darkred' if edge in paired_edges else 'black'
            u.directed_line(ax, p1, p2, linewidth=2.5, color=color, arrow_alpha=1.0)

single_cell = '898f50703cbffff'

with u.svg('figs/single_cell_directed_edges.svg') as ax:
    for edge in h3.origin_to_directed_edges(single_cell):
        p1, p2 = u.scale_edge(edge, theta=1.0)
        u.directed_line(ax, p1, p2, linewidth=2.5, color='black', arrow_alpha=1.0)

    center_lat, center_lon = h3.cell_to_latlng(single_cell)
    ax.text(
        center_lon, center_lat, 'origin',
        ha='center', va='center',
        fontsize=12, fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2),
    )



