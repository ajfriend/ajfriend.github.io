import h3
import numpy as np
import matplotlib.pyplot as plt
import util as u

SHOW_AXIS = False

cells = [
    '898f50703cbffff',
    '898f50703cfffff',
    '898f50703c3ffff',
    '898f50703c7ffff',
]
edges = u.cells_to_edges(cells)


edges1 = edges - u.twinning(
    '1198f50703c3ffff',
    '1198f50703cbffff',
    # '1298f50703c3ffff',
    # '1398f50703c3ffff',
    # '1298f50703c7ffff',
)
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
u.save_svg(fig, 'figs/four_cells_0.svg')


edges1 = edges - u.twinning(
    '1198f50703c3ffff',
    '1198f50703cbffff',
    '1298f50703c3ffff',
    # '1398f50703c3ffff',
    # '1298f50703c7ffff',
)
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
u.save_svg(fig, 'figs/four_cells_1.svg')


edges1 = edges - u.twinning(
    '1198f50703c3ffff',
    '1198f50703cbffff',
    '1298f50703c3ffff',
    '1398f50703c3ffff',
    # '1298f50703c7ffff',
)
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
u.save_svg(fig, 'figs/four_cells_2.svg')

edges1 = edges - u.twinning(
    '1198f50703c3ffff',
    '1198f50703cbffff',
    '1298f50703c3ffff',
    '1398f50703c3ffff',
    '1298f50703c7ffff',
)
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
u.save_svg(fig, 'figs/four_cells_3.svg')

edges1 = edges - u.twinning(
    '1198f50703c3ffff',
    '1198f50703cbffff',
    '1298f50703c3ffff',
    # '1398f50703c3ffff',
    '1298f50703c7ffff',
)
fig, ax = u.figure()
ax.set_aspect('equal')
if not SHOW_AXIS:
    ax.axis('off')
u.plot_edges(edges1, ax=ax)
u.save_svg(fig, 'figs/four_cells_4.svg')
