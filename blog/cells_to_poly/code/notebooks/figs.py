import h3
import util as u

cells = [
    '8a806a7660effff',
    '8a806a7660c7fff',
    '8a806a7660e7fff',
    '8a806a7660f7fff',
]


edges = set(
    e
    for c in cells
    for e in h3.origin_to_directed_edges(c)
)

# edges1 = edges - set([
#     '1182830828bfffff', '1682830829dfffff',
#     '118283082d7fffff', '16828308299fffff',
#     # '12828308299fffff', '1582830829dfffff',
#     # '138283082d7fffff', '1482830829dfffff',
#     # '128283082d7fffff', '1582830828bfffff',
# ])

# Create figure and fill cells with pastel colors
fig, ax = u.figure()
ax.set_aspect('equal')
colors = ['blue', 'blue', 'blue', 'blue']
for cell, color in zip(cells, colors):
    u.fill_cell(ax, cell, color=color)

# Fill gaps between cells (one edge from each removed pair)
# u.fill_gap(ax, '1182830828bfffff', color='blue')
# u.fill_gap(ax, '118283082d7fffff', color='blue')
# u.fill_gap(ax, '12828308299fffff', color='blue')
# u.fill_gap(ax, '138283082d7fffff', color='blue')

# Draw edges on top
u.plot_edges(edges, ax=ax)
fig.savefig('bah.png', dpi=600)
