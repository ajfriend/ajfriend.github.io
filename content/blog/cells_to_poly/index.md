---
title: "[WIP] Making H3's cells-to-polygon faster"
date: 2026-01-09
toc: true
---

**Note**: This post is currently a quick-and-dirty attempt at explaining the algorithm
behind [cellsToMultiPolygon core algorithm #1113 · uber/h3](https://github.com/uber/h3/pull/1113). My plan is to grow this into a
proper blog post with more context, background, etc.


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
I wrote up my thoughts on "ideal" spherical polygons in [another post](/blog/sphere_poly/), but to summarize, we want to output spherical polygons such that:

- polygons consist of ordered loops of points on a sphere (lon/lat points)
- polygons have one "outer" loop, with points oriented in counter-clockwise order, and zero or more "inner" loops, with points going clockwise (see the image above)
- we can handle "large" cell sets, where resulting polygons may cross the antimeridian, enclose the poles, or be larger than a hemisphere

# H3 edges

How do we do this translation? For any h3 cell, we can get the simple polygon lat/lng points that describe its region. I want to avoid floating point comparisons, so instead we'll look at the set of edges. For any edge, you can get the same lat/lng points.

Edges are directed:

TODO: origin destination, and then switch them below. describe right hand rule. Maybe these aren't shrunk yet.

{{< fig src="code/figs/directed_edge.svg" >}}


whenever we're plotting more than one cell, where the edges might conflict...

To avoid plotting two opposite edges on top of each other, we'll shrink
each edge towards its origin cell's center:

{{< fig src="code/figs/two_cells_edges.svg" >}}

Maybe this is where we mention we can put the edges in order? Maybe not...
maybe we hold that off until after the cancellation talk.


# General idea: cancel out the edges

So how do we get the outline? Well, looking at edges, we see we can just
cancel out the pairs and the outline remains.

However, we don't have the order of lat/lng points, we don't know what the loops are, which loops are part of which polygon, and which loops are outside and which are holes.



in this version, we just show sets of edges first.

compute the reverse. look for collisions.
ok, but this just gives us the bag of edges.
how do we get a loop in order?

we can go back to the idea of trying to figure out which one is which.

but what if we can exploit the fact that these edges are already sorted
in each cell. (ed: how do we demonstrate the loop?)

the hash table finds the `Arc` (pair of arcs) we want to work on. we once that's in hand,
we can do a few other things, like modify the linked-loop and keep
track of connected components.


# Rings of edges

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

