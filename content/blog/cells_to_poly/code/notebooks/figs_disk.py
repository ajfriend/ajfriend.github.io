import h3
import numpy as np
import matplotlib.pyplot as plt
import util as u

SHOW_AXIS = False

h = '898f50703cbffff'
cells = h3.grid_disk(h, 1)

edges = u.cells_to_edges(cells)

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges, ax=ax)
fig.savefig('figs/disk_0.svg', bbox_inches='tight')



edges0 = u.cells_to_edges([h])
edges0 = u.twinning(*edges0)
edges1 = edges - edges0

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
fig.savefig('figs/disk_1.svg', bbox_inches='tight')


edges1 = edges - u.reverse_set(edges)

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
fig.savefig('figs/disk_2.svg', bbox_inches='tight')
