import util as u

cells1 = ['898f50703cbffff']
cells2 = ['898f50703cbffff', '898f50703cfffff']

with u.svg('figs/single_cell.svg') as ax:
    edges = u.cells_to_edges(cells1)
    u.plot_edges(edges, ax=ax)

with u.svg('figs/two_cells_before.svg') as ax:
    edges = u.cells_to_edges(cells2)
    u.plot_edges(edges, ax=ax)

with u.svg('figs/two_cells_after.svg') as ax:
    edges = u.cells_to_edges(cells2)
    edges -= u.reverse_set(edges)
    u.plot_edges(edges, ax=ax)
