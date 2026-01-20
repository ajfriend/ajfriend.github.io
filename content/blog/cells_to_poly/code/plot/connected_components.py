import util as u
import h3

cells = [
    '8966dbda96bffff',
    '8966dbda947ffff',
    '8966dbda94fffff',
    '8966dbdabb3ffff',
    '8966dbdaba3ffff',
    '8966dbdabafffff',
    '8966dbc36dbffff',
    '8966dbc36c3ffff',
    '8966dbc36d7ffff',
    '8966dbc369bffff',
    '8966dbda967ffff',
    '8966dbda977ffff',
    '8966dbda973ffff',
    '8966dbdababffff',
    '8966dbdab17ffff',
    '8966dbdab13ffff',
    '8966dbdabc7ffff',
    '8966dbdabd7ffff',
    '8966dbdab9bffff',
    '8966dbdab93ffff',
    '8966dbda82fffff',
    '8966dbda827ffff',
    '8966dbda953ffff',
    '8966dbda957ffff',
    '8966dbda943ffff',
    '8966dbda94bffff',
    '8966dbdab97ffff',
    '8966dbdabbbffff',
    '8966dbdab87ffff',
    '8966dbda903ffff',
    '8966dbda907ffff',
]

edges = u.cells_to_edges(cells)

with u.svg('figs/conn_comp.svg', size=8) as ax:
    edges1 = edges - u.twinning(
        # '1198f50703c3ffff',
        # '1198f50703cbffff',
    )
    u.plot_edges(edges1, ax=ax, arrow_scale=12)

