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
fig.savefig('figs/single_cell.svg', bbox_inches='tight')


fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
edges = u.cells_to_edges(['898f50703cbffff', '898f50703cfffff'])
u.plot_edges(edges, ax=ax)
fig.savefig('figs/two_cells_before.svg', bbox_inches='tight')


fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
edges = u.cells_to_edges(['898f50703cbffff', '898f50703cfffff'])
edges -= u.reverse_set(edges)
u.plot_edges(edges, ax=ax)
fig.savefig('figs/two_cells_after.svg', bbox_inches='tight')


# TODO: add labels `a` and `b` to the pair of edges that are going to cancel.
# TODO: add label `a^-` and `a^+` to the edges before and after `a` in its loop. the same for b
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
edges = u.cells_to_edges(['898f50703cbffff', '898f50703cfffff'])
u.plot_edges(edges, ax=ax)
fig.savefig('figs/two_cells_before_labels.svg', bbox_inches='tight')
