import h3
import numpy as np
import matplotlib.pyplot as plt
import util as u

SHOW_AXIS = False

edges = u.cells_to_edges(['898f50703cbffff'])

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges, ax=ax)
u.save_svg(fig, 'figs/single_cell.svg')


fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
edges = u.cells_to_edges(['898f50703cbffff', '898f50703cfffff'])
u.plot_edges(edges, ax=ax)
u.save_svg(fig, 'figs/two_cells_before.svg')


fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
edges = u.cells_to_edges(['898f50703cbffff', '898f50703cfffff'])
edges -= u.reverse_set(edges)
u.plot_edges(edges, ax=ax)
u.save_svg(fig, 'figs/two_cells_after.svg')
