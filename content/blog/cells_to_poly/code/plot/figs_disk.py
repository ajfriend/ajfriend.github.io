import h3
import util as u

h = '898f50703cbffff'
cells = h3.grid_disk(h, 1)
edges = u.cells_to_edges(cells)

with u.svg('figs/disk_0.svg') as ax:
    u.plot_edges(edges, ax=ax)

with u.svg('figs/disk_1.svg') as ax:
    edges0 = u.cells_to_edges([h])
    edges0 = u.twinning(*edges0)
    edges1 = edges - edges0
    u.plot_edges(edges1, ax=ax)

with u.svg('figs/disk_2.svg') as ax:
    edges1 = edges - u.reverse_set(edges)
    u.plot_edges(edges1, ax=ax)
