import util as u

cells = [
    '898f50703cbffff',
    '898f50703cfffff',
    '898f50703c3ffff',
    '898f50703c7ffff',
]
edges = u.cells_to_edges(cells)

with u.svg('figs/four_cells_0.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f50703c3ffff',
        '1198f50703cbffff',
    )
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/four_cells_1.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f50703c3ffff',
        '1198f50703cbffff',
        '1298f50703c3ffff',
    )
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/four_cells_2.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f50703c3ffff',
        '1198f50703cbffff',
        '1298f50703c3ffff',
        '1398f50703c3ffff',
    )
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/four_cells_3.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f50703c3ffff',
        '1198f50703cbffff',
        '1298f50703c3ffff',
        '1398f50703c3ffff',
        '1298f50703c7ffff',
    )
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/four_cells_4.svg') as ax:
    edges1 = edges - u.twinning(
        '1198f50703c3ffff',
        '1198f50703cbffff',
        '1298f50703c3ffff',
        '1298f50703c7ffff',
    )
    u.plot_edges(edges1, ax=ax)
