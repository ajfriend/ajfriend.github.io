import h3
import numpy as np
import matplotlib.pyplot as plt
import util as u

SHOW_AXIS = False

h = '898f50703cbffff'
cells = h3.grid_ring(h, 1)
edges = u.cells_to_edges(cells)

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges, ax=ax)
fig.savefig('figs/ring_0.svg', bbox_inches='tight')



edges1 = edges - u.twinning(
    '1198f5070227ffff',
    '1198f50703dbffff',
    '1298f50703cfffff',
    '1298f50703dbffff',
    '1398f5070237ffff',
    # '1398f50703c3ffff',
)

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
fig.savefig('figs/ring_1.svg', bbox_inches='tight')


edges1 = edges - u.twinning(
    '1198f5070227ffff',
    '1198f50703dbffff',
    '1298f50703cfffff',
    '1298f50703dbffff',
    '1398f5070237ffff',
    '1398f50703c3ffff',
)

fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
fig.savefig('figs/ring_2.svg', bbox_inches='tight')
