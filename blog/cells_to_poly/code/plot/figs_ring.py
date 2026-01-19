import h3
import util as u

h = '898f50703cbffff'
cells = h3.grid_ring(h, 1)
edges = u.cells_to_edges(cells)

with u.svg('figs/ring_0.svg') as ax:
    u.plot_edges(edges, ax=ax)

with u.svg('figs/ring_1.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f5070227ffff',
        '1198f50703dbffff',
        '1298f50703cfffff',
        '1298f50703dbffff',
        '1398f5070237ffff',
    )
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/ring_2.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f5070227ffff',
        '1198f50703dbffff',
        '1298f50703cfffff',
        '1298f50703dbffff',
        '1398f5070237ffff',
        '1398f50703c3ffff',
    )
    u.plot_edges(edges1, ax=ax)
