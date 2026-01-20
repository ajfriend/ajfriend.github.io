---
title: "[WIP] Making H3's cells-to-polygon faster"
date: 2026-01-09
toc: true
---

**Note**: This post is currently a quick-and-dirty attempt at explaining the algorithm
behind [cellsToMultiPolygon core algorithm #1113 · uber/h3](https://github.com/uber/h3/pull/1113). My plan is to grow this into a
proper blog post with more context, background, etc.

TODO: note the python implementation


# Goal: H3 cells to spherical polygons

A collection of [H3 cells](https://h3geo.org/) describes a subset of the globe,
and a common operation is to translate that set of cells into spherical polygons
(e.g., a [GeoJSON](https://geojson.org/) `MultiPolygon`) outlining the same region.

<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 1rem;">
{{< globe_map data="data/intro_cells.json" width="400" >}}
<span style="font-size: 2rem;">→</span>
{{< globe_map data="data/intro_poly.json" width="400" arrowStep="3" >}}
</div>
{{< caption >}}A set of H3 cells maps to three polygons; two with no holes, and one with three holes. Drag the globe to rotate; double click to reset.{{< /caption >}}

Alternatively, in code, the translation might look like:

<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 2rem;">
<div>

```python
cells = [
  '81463ffffffffff',
  '8146bffffffffff',
  '81713ffffffffff',
  '81467ffffffffff',
  '8147bffffffffff',
  ...
]
```

</div>
<span style="font-size: 2rem;">→</span>
<div>

```json
{
  "type": "MultiPolygon",
  "coordinates": [
    [[[-179.1, 43.3], ...]],
    [[[-137.1, 34.7], ...]],
    [[[-147.8, 9.6], ...]]
  ]
}
```

</div>
</div>

GeoJSON is just one format we can use for describing spherical polygons,
but the algortihm we cover here here is applicable
to any similar format, and its easy to translate between them.
I wrote up my thoughts on ["ideal" spherical polygons in another post](/blog/sphere_poly/), but to summarize, we want to output spherical polygons such that:

- polygons consist of ordered loops of points on a sphere (lon/lat points)
- polygons have one "outer" loop, with points oriented in counter-clockwise order, and zero or more "inner" loops, with points going clockwise (see the image above)
- we can handle "large" cell sets, where resulting polygons may cross the antimeridian, enclose the poles, or be larger than a hemisphere

# H3 cells and edges

How do we do this translation? Let's start by considering components of
H3 cells and what we can do with them.

For any H3 cell, we can get the simple polygon of lat/lng points that describe it. In the H3 C library or in the bindings, you can get those points
with the [`cellToBoundary()`](https://h3geo.org/docs/api/indexing#celltoboundary) function. We *could* operate on those points, gathering them for each cell, and using them to construct the MultiPolygon boundary, but this **continous** approach would involve floating point comparisons and error tolerances.
As an alternative, we might look for a **discrete** approach, with discrete objects that are either present or not, can be hashed, and compared for exact, unambiguous equality. The **directed edges** that make up the H3 cell boundary are a great candidate.

## Directed edge preliminaries

In H3, a directed edge can be thought of as the boundary between two adjacent cells. Each edge has an **origin** cell and a **destination** cell, which we can
provide to [`cellsToDirectedEdge()`](https://h3geo.org/docs/api/uniedge#cellstodirectededge) to get the edge index.
We can form the **opposite** or **reversed** edge by swapping the origin and destination cells, or by calling [`reverseDirectedEdge()`](https://github.com/uber/h3/pull/1098).

The convention we'll use in this post will be to plot an arrow along the edge,
with the origin cell on the left (from the arrow's perspective.)

{{< fig src="code/figs/directed_edge.svg" >}}
{{< caption >}}An H3 directed edge and its reverse edge. Note the orientation of the arrow with respect to the origin cell.{{< /caption >}}

Also, we can get the lat/lng points that make up the edge from [`directedEdgeToBoundary()`](https://h3geo.org/docs/api/uniedge#directededgetoboundary), and they're returned in the order that aligns with the arrow: first point at the tail of the arrow, and last point at the tip. (Note that due to icosahedron distortions, some H3 edges have a "kink" in them, and thus have three points instead of just two.)

Plotting the edges for a single H3 hexagon, we see that these components align with [the right-hand rule for spherical polygons
that GeoJSON conforms to](https://gis.stackexchange.com/questions/259944/polygons-and-multipolygons-should-follow-the-right-hand-rule). That is,
if we take the edges in order and extract their lat/lng points, we get a sequence
of points in counter-clockwise order around the cell. Note that the last
point of an edge is the first point of the following edge.

{{< fig src="code/figs/single_cell_directed_edges.svg" >}}

Note that this almost acheives our goal (at least for a single cell): we can recover a list of lat/lng points in counter-clockwise order denoting the outer
loop of a spherical polygon.

However, the order of the edges is important. Note that
[`originToDirectedEdges()`](https://h3geo.org/docs/api/uniedge#origintodirectededges) doesn't automatically return directed edges
in counter-clockwise order, but we can permute them so that that's the case---and the same permutation works for every H3 cell. We'll get into using
the ordering later on, but for now I'll just note that we hard code the permutation in the PR with something like

```c
static const uint8_t idxh[6] = {0, 4, 3, 5, 1, 2};  // hexagons
static const uint8_t idxp[5] = {0, 1, 3, 2, 4};     // pentagons
```

Whenever we're plotting more than one cell, edges will overlap with their opposites. To visually distinguish them in most of the plots below, we'll
shrink the directed edges towards the center of their origin cell:

{{< fig src="code/figs/two_cells_edges.svg" >}}
{{< caption >}}Two cells (blue) with their associated directed edges (black/red) shrunk towards the centers to avoid overlaps. Note the symmetric pair of opposite edges (red).{{< /caption >}}

We'll refer to an edge and its reversed edge a **symmetric pair**.


# General idea: remove symmetric pairs

That last image suggest an idea: for a set of cells $C$, if we get the set of all
of the directed edges with origins belonging to $C$, we can then remove all
the symmetric pairs (i.e., remove all the "internal" edges), and what we end up with is the set of directed edges making up the boundary of the polygon we're looking for.

<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 0rem;">
{{< fig src="code/figs/disk_0.svg" width="300px" >}}
<span style="font-size: 2rem;">→</span>
{{< fig src="code/figs/disk_2.svg" width="300px" >}}
</div>
{{< caption >}}Eliminating symmetric pairs of edges leaves us with the set of edges on the boundary.{{< /caption >}}

Note that, so far, we've just described how to get the **set** of boundary edges.
There's no notion yet of how we make sure the lat/lng points in the outer boundary are in counter-clockwise order, how we handle holes, or how we figure
out which edges are part of which loop or polygon. We'll get to that below,
but first we'll discuss the cancellation logic. (But do notice that if the edges *were* put in the correct order, we would have our desired counter-clockwise loop
for this polygon's outer looop.)

## Example: one hole

Here's the symmetric pair cancellation procedure on another example.
We start with 6 cells, with a center cell missing, and consider the full set of
their edges:
{{< fig src="code/figs/ring_0.svg" >}}
{{< caption >}}Initial set of edges from six cells, with a central cell missing. Loops initially all counter-clockwise.{{< /caption >}}

Eliminating all symmetric pairs but one leaves us with a single loop in
counter-clockwise order. (This figure doesn't represent the actual locations of the edge endpoints since we've shrunk them, so it's true that this loop is degenerate in the sense that the symmetric pair of edges exactly overlap one another, but we're OK with that for this intermediate state, since they're about to be removed anyway.)
{{< fig src="code/figs/ring_1.svg" >}}
{{< caption >}}A (geometrically) degenerate, but intermediate counter-clockwise loop. {{< /caption >}}

When the final symmetric pair is removed, we're left with two rings of edges: one outer loop in counter-clockwise order and one inner loop in clockwise order, deoting the hole missing from the polygon:
{{< fig src="code/figs/ring_2.svg" >}}
{{< caption >}}An outer loop (counter-clockwise) and one hole loop (clockwise).{{< /caption >}}

The next major sections describe how we recover the additional information
we need (beyond just the unordered set of edges) to describe the polygon.

## Implementation notes: hash table

In Python, just getting the set of cells and canceling out the symmetric
pairs is pretty trivial. I would look something like:

```python
import h3

edges = {
    e
    for h in cells
    for e in h3.origin_to_directed_edges(h)
}
reversed_edges = {
    h3.reverse_directed_edge(e)
    for e in edges
}
boundary_edges = edges - reversed_edges
```

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), we need to do a
little more work, and set up the data structures we'll use to keep track of the
additional information we'll need to create well-formed polygons.

For each edge, we create an `Arc` struct to capture all the relevant information
for an edge. We'll only focus on the parts we need for symmetric pair cancellation in this section.

```c
typedef struct Arc {
    H3Index id;  // directed edge index
    // ... (additional state)
} Arc;
```

For each cell in the input set, we create its 5 or 6 `Arc`s and store
them in an `ArcSet`, so that we can iterate through the `Arc`/edges later on by
looping through an array.

In addition to iterating through the `Arc`s, we'll want to be able to quickly
look them up by their H3 index so that we can remove symmetric pairs.
For this, we create a simple hash table,
corresponding to `buckets` and `numBuckets`.

```c
typedef struct {
    int64_t numArcs;
    Arc *arcs;
    int64_t numBuckets;  // = 10 * numArcs
    Arc **buckets;
} ArcSet;
```

After initializing the `ArcSet` with all the intial loops from each individual
cell, we loop through the `Arc`s (that haven't been removed yet), compute
their reversed edge, look it up with the hash table, and mark `arc.isRemoved = true`. (We also do some additional work that we'll get to in the following sections.)

For some `Arc` called `a`, we can get a pointer to its reverse edge (if it exists in the set) using `findArc`:

```c
H3_EXPORT(reverseDirectedEdge)(a->id, &reversedEdge);
Arc *b = findArc(arcset, reversedEdge);
```

We can do what we want with this pair of edges `a` and `b`. For now, the first
step is to mark them both as being removed:

```c
a->isRemoved = true;
b->isRemoved = true;
```

We use a simple linear probing scheme with `numBuckets = 10 * numArcs` to keep collisions low. In the future, an improved algorithm could use less memory without sacrificing lookup speed. (Suggestions welcome!)

As mentioned, so far, this just covers keeping track of the **set** of
edges we care about. Now we'll discuss the additional strucutre we need
to keep track of.


# Rings of edges

we can go back to the idea of trying to figure out which one is which.

but what if we can exploit the fact that these edges are already sorted
in each cell. (ed: how do we demonstrate the loop?)

the hash table finds the `Arc` (pair of arcs) we want to work on. we once that's in hand,
we can do a few other things, like modify the linked-loop and keep
track of connected components.



Each H3 cell has 6 directed edges (5 for pentagons) that we can enumerate
in counter-clockwise order. We store each edge in an `Arc` struct, using
`next` and `prev` pointers to form a doubly-linked list of the edges surrounding that cell:

```c
typedef struct Arc {
    H3Index id;       // directed edge index
    struct Arc *next;
    struct Arc *prev;
    // ...
} Arc;
```

H3's `originToDirectedEdges` returns edges in a fixed order, but not
counter-clockwise. We reorder them:

```c
static const uint8_t idxh[6] = {0, 4, 3, 5, 1, 2};  // hexagons
static const uint8_t idxp[5] = {0, 1, 3, 2, 4};     // pentagons
```

{{< fig src="code/figs/single_cell.svg" >}}

For each cell in the input set, we create its 5 or 6 arcs and doubly-link them into a loop of `Arc`s (work done by `cellToEdgeArcs`). We store all the `Arc`s in an `ArcSet` so that we can iterate through the `Arc`/edges them later. Note that, at this point, the loops from different cells are disjoint from one another.

```c
typedef struct {
    int64_t numArcs;
    Arc *arcs;
    // ...
} ArcSet;
```

For this loop, and the loops we'll have later on, we can call `directedEdgeToBoundary` to get the lat/lng coordinates of the edge vertices.

# Edge cancellation

The main idea of the algorithm is that we start with valid loops (small loops around cells), find pairs of edges that cancel each other out,
remove the pairs of edges, and stitch together the loops---all while
**maintaining valid loops the whole time**.

For example, if we were to start with two neighboring cells, with two disjoint loops, the `ArcSet` would initially correspond to this picture:

{{< fig src="code/figs/two_cells_before.svg" caption="Initial state of edges for two cells." >}}

After canceling the pair of edges, the `ArcSet` would look like this:

{{< fig src="code/figs/two_cells_after.svg" width="600px" caption="After canceling pairs of edges." >}}

Note that the edges stay in a counter-clockwise loop.

## Finding edge pairs

Every directed edge has an edge representing the opposite direction. To find pairs, we iterate through all arcs,
compute the reverse with `reverseDirectedEdge`, and look it up in a hash table:

```c
H3_EXPORT(reverseDirectedEdge)(a->id, &reversedEdge);
Arc *b = findArc(arcset, reversedEdge);
```

If `b` exists, we've found a pair to cancel. We mark both as removed with `isRemoved = true` in the `Arc` struct.

The hash table lives in `ArcSet`:

```c
typedef struct {
    int64_t numArcs;
    Arc *arcs;
    int64_t numBuckets;  // = 10 * numArcs
    Arc **buckets;
} ArcSet;
```

We use a simple linear probing scheme with `numBuckets = 10 * numArcs` to keep collisions low. In the future, an improved algorithm could use less memory without sacrificing lookup speed.

## Loop surgery

When canceling edges `a` and `b`, we splice them out by reconnecting their neighbors.

The edges in the loops are initially chained like:

$$
\begin{aligned}
a^- &\to a \to a^+ \\
b^- &\to b \to b^+
\end{aligned}
$$

{{< fig src="code/figs/two_cells_before_labels.svg" >}}

After removing edges `a` and `b`, we recconect their surrounding edges like
the following, which merges the two loops into one counter-clockwise loop,
updating the doubly-linked list appropriately.

$$
\begin{aligned}
a^- &\to b^+ \\
b^- &\to a^+
\end{aligned}
$$

{{< fig src="code/figs/two_cells_after_labels.svg" >}}


In the C code, this looks like the following, where `a` and `b` are `Arc` structs:

```c
a->next->prev = b->prev;
a->prev->next = b->next;
b->next->prev = a->prev;
b->prev->next = a->next;
```

## Other edge cancellation examples

Luckily, the loop surgery logic above works in all possible cases.


{{< fig src="code/figs/four_cells_0.svg" >}}
{{< fig src="code/figs/four_cells_1.svg" >}}
{{< fig src="code/figs/four_cells_2.svg" >}}
{{< fig src="code/figs/four_cells_3.svg" >}}

Note that we can remove the edges in any order. Even the following is
a completely valid set of two linked-loops (even though the edges in the middle don't enclose any area and will need to be ultimately removed before we form proper polygons):

{{< fig src="code/figs/four_cells_4.svg" >}}

### Disk

{{< fig src="code/figs/disk_0.svg" >}}

Removing the edges associated with the center cell leaves a single
ring (with 6 degenerate pairs left to be removed):
{{< fig src="code/figs/disk_1.svg" >}}

{{< fig src="code/figs/disk_2.svg" >}}


### Hole

Note that canceling edges might split up rings:

{{< fig src="code/figs/ring_0.svg" >}}
{{< fig src="code/figs/ring_1.svg" >}}
{{< fig src="code/figs/ring_2.svg" >}}


# Connected components partition loops into polygons

TODO: edges example with multiple loops and polygons.

Plotting: make the connected components easier by just plotting the whole
H3 cell, then i don't have to do the bits to connect the shrunken cells.

# Which loop is "outside"?

In a polygon, one loop is *special*. The outer loop. the rest are holes.
Actually, not relaly that special. any loop can be the outer loop and still mathematical describe the same polygon, even if it is an unintuitive format.


a tricky one might look like: blah


# Notes

- maybe do a **Summary** section at the end of each, and also a **Code** section, that might ligthen it up? or is it helpful to have the code snippets in the doc inline?
- separate out with Code section. can link multiple implementations. include the python one
- end with some fun, tricky examples

