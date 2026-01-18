import h3
import util as u

cells = ['898f50703cbffff', '898f50703cfffff']

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
            u.directed_line(ax, p1, p2, linewidth=2.5)
