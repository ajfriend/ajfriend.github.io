import h3
import matplotlib.pyplot as plt
import util as u

cells = ['898f50703cbffff', '898f50703cfffff']

# Get the shared edge (from cell 0 to cell 1)
edge = h3.cells_to_directed_edge(cells[0], cells[1])
edge_rev = h3.cells_to_directed_edge(cells[1], cells[0])

def plot_cell_outline(ax, cell, color='black', linewidth=1.5):
    """Plot the full outline of a cell (not shrunk)."""
    boundary = h3.cell_to_boundary(cell)
    xs = [p[1] for p in boundary] + [boundary[0][1]]
    ys = [p[0] for p in boundary] + [boundary[0][0]]
    ax.plot(xs, ys, color=color, linewidth=linewidth)

def plot_directed_edge_full(ax, edge):
    """Plot a directed edge at full size with an arrow."""
    bd = h3.directed_edge_to_boundary(edge)
    u.directed_line(ax, bd[0], bd[-1], linewidth=4, arrow_scale=35, arrow_alpha=1.0)

def label_cell(ax, cell, label):
    """Add a label at the center of a cell."""
    center = h3.cell_to_latlng(cell)
    ax.text(
        center[1], center[0], label,
        ha='center', va='center',
        fontsize=12, fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', pad=2),
    )

def setup_ax(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    ax.axis('off')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 8))

# Plot 1: cell[0] is origin, cell[1] is destination
for cell in cells:
    plot_cell_outline(ax1, cell, color='darkblue', linewidth=2)
plot_directed_edge_full(ax1, edge)
label_cell(ax1, cells[0], 'origin')
label_cell(ax1, cells[1], 'destination')
setup_ax(ax1)

# Plot 2: cell[1] is origin, cell[0] is destination (reversed)
for cell in cells:
    plot_cell_outline(ax2, cell, color='darkblue', linewidth=2)
plot_directed_edge_full(ax2, edge_rev)
label_cell(ax2, cells[1], 'origin')
label_cell(ax2, cells[0], 'destination')
setup_ax(ax2)

plt.tight_layout()
u.save_svg(fig, 'figs/directed_edge.svg')
plt.close(fig)
