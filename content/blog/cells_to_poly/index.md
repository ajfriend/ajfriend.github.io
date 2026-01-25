---
title: "[WIP] Making H3's cells-to-polygon faster"
date: 2026-01-24
toc: true
---

**Note**: This post is currently a quick-and-dirty attempt at explaining the algorithm
behind the PR [uber/h3 #1113](https://github.com/uber/h3/pull/1113). My plan is to grow this into a
proper blog post with more context, background, etc.

I also have a Python version of this algorithm shared at https://github.com/ajfriend/h3c2p


# Goal: H3 cells to spherical polygons

A collection of [H3 cells](https://h3geo.org/) describes a subset of the globe,
and an operation we often want to do is to translate that set into an alternative representation of that region as a collection of spherical polygons
(e.g., a [GeoJSON](https://geojson.org/) `MultiPolygon`).

<div style="display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 1rem;">
{{< globe_map data="data/intro_cells.json" width="400" >}}
<span style="font-size: 2rem;">→</span>
{{< globe_map data="data/intro_poly.json" width="400" arrowStep="3" >}}
</div>
{{< caption >}}A set of H3 cells maps to three polygons; two with no holes, and one with three holes. Outer loops are oriented counter-clockwise and holes are oriented clockwise. Drag the globe to rotate; double click to reset.{{< /caption >}}

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
    [[[-147.8, 9.60], ...]]
  ]
}
```

</div>
</div>

GeoJSON is just one format we can use for describing spherical polygons,
but the algorithm we cover here is applicable
to any similar format, and its easy to translate between them.
I wrote up my thoughts on ["ideal" spherical polygons in another post](/blog/sphere_poly/), but to summarize, we want to output spherical polygons such that:

- polygons consist of ordered loops of points on a sphere (lon/lat points)
- polygons have one "outer" loop, with points oriented in counter-clockwise order, and zero or more "inner" loops, with points going clockwise (see the image above)
- we can handle "large" cell sets, where resulting polygons may cross the antimeridian, enclose the poles, or be larger than a hemisphere

# Components of H3 cells

How do we do this translation? Let's start by considering components of
H3 cells and what we can do with them.

Cells are already polygons themselves. So how do you build a big polygon from smaller ones? Pull them apart and put the pieces back together! For what we can break these H3 cells down to, we have a couple of options:

1. H3 cell lat/lng vertices (continuous)
2. H3 [vertex mode](https://h3geo.org/docs/library/index/vertex) (discrete)
3. H3 [directed edge mode](https://h3geo.org/docs/api/uniedge) (discrete).

For any H3 cell, we can get the simple polygon of lat/lng points that describe it. In the H3 C library or in the bindings, you can get those points
with the [`cellToBoundary()`](https://h3geo.org/docs/api/indexing#celltoboundary) function. We *could* operate on those points, gathering them for each cell, and using them to construct the `MultiPolygon` boundary, but this **continuous** approach would involve floating point comparisons and error tolerances.
As an alternative, we might look for a **discrete** approach, with discrete objects that are either present or not, can be hashed, and compared for exact, unambiguous equality. The directed edges that make up the H3 cell boundary are a great candidate. We could also probably work with H3 vertex mode, but as
you'll see below, the ability to "reverse" directed edges allows for some very
natural operations, so that's what we'll use.

# Directed edge preliminaries

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
in counter-clockwise order, but we *can* permute them so that that is the case---and the same permutation works for every H3 cell. We'll get into using
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


# Main idea: remove symmetric pairs

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
for this polygon's outer loop.)

## Example: one hole

Here's the symmetric pair cancellation procedure on another example.
We start with 6 cells, with a center cell missing, and consider the full set of
their edges:
{{< fig src="code/figs/ring_0.svg" >}}
{{< caption >}}Initial set of edges from six cells, with a central cell missing. Loops initially all counter-clockwise.{{< /caption >}}

Eliminating all symmetric pairs except for one leaves us with a single loop in
counter-clockwise order. (This figure doesn't represent the actual locations of the edge endpoints since we've shrunk them, so it's true that this loop is degenerate in the sense that the symmetric pair of edges exactly overlap one another, but we're OK with that for this intermediate state, since they're about to be removed anyway.)
{{< fig src="code/figs/ring_1.svg" >}}
{{< caption >}}A (geometrically) degenerate, but intermediate counter-clockwise loop. {{< /caption >}}

When the final symmetric pair is removed, we're left with two rings of edges: one outer loop in counter-clockwise order and one inner loop in clockwise order, denoting the hole missing from the polygon:
{{< fig src="code/figs/ring_2.svg" >}}
{{< caption >}}An outer loop (counter-clockwise) and one hole loop (clockwise).{{< /caption >}}

The next major sections describe how we recover the additional information
we need (beyond just the unordered set of edges) to describe the polygon.

## Implementation notes: hash table

### Python

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

### C

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), we need to do a
little more work to set up the hashing we'll use to find the symmetric pairs, and we also need to set up the data structures we'll use to keep track of the
additional information we'll need to create well-formed polygons.

For each edge, we create an `Arc` struct to capture all the relevant information
for an edge. We'll only focus on the parts we need for symmetric pair cancellation in this section.

```c
typedef struct Arc {
    H3Index id;  // directed edge index
    // ...
} Arc;
```

For each cell in the input set, we create its 5 or 6 `Arc`s and store
them in an `ArcSet`, so that we can iterate through the `Arc`/edges later on by
looping through an array.

In addition to iterating through the `Arc`s, we'll want to be able to quickly
look them up by their H3 index so that we can remove symmetric pairs.
For this, we create a simple hash table,
corresponding to `buckets` and `numBuckets` in `ArcSet`:

```c
typedef struct {
    int64_t numArcs;
    Arc *arcs;
    int64_t numBuckets;  // = 10 * numArcs
    Arc **buckets;
} ArcSet;
```

The `createArcSet()` function initializes the `Arc`s from an array of H3 cells,
and hashes all the edges for quick random lookup.

For some `Arc` called `a`, we can get a pointer to its reverse edge (if it exists in the set) using `findArc`:

```c
H3_EXPORT(reverseDirectedEdge)(a->id, &reversedEdge);
Arc *b = findArc(arcset, reversedEdge);
```

We use a simple linear probing scheme with `numBuckets = 10 * numArcs` to keep collisions low. In the future, an improved algorithm could use less memory without sacrificing lookup speed. (Suggestions welcome!)

After initializing the `ArcSet`, we can perform the edge cancellation with the C function `cancelArcPairs()`, which roughly follows the pseudocode:

1. loop through the `Arc`s (that haven't been removed yet) via the `ArcSet.arcs` array
2. for each `Arc`, `a`, compute its reversed edge like `e_b = reverseDirectedEdge(a.id)`
3. find the corresponding `Arc` via the hash table with `Arc *b = findArc(arcset, e_b)`
4. with both `Arc`s in hand, we can mark both as removed:
    ```c
    a->isRemoved = true;
    b->isRemoved = true;
    ```
5. Note that we do some additional work around loops and connected components, but we'll cover that in the upcoming sections.

The edges remaining afer cancellation (those with `isRemoved = false`) are the
ones that make up the polygon boundaries.
But note that this logic just amounts to keeping track of the **set** of
boundary edges.  Next, we'll discuss the additional structure we need
to keep track of to form the polygons.


# Loops of edges

Above, we found the **set** of edges that make up the polygon boundary.
But how do we construct or maintain the ordering of edges so that we can construct the ordered loops of lat/lng points that make up polygon outer loops
and holes?

Recall from ["Directed edge preliminaries"](#directed-edge-preliminaries) that we can order the edges of individual cells so that they are in counter-clockwise order:

{{< fig src="code/figs/single_cell.svg" >}}

To keep track of this ordering, each `Arc` maintains `prev` and `next` pointers,
which we use to construct doubly-linked lists of `Arc`s:
```c
typedef struct Arc {
    H3Index id;       // directed edge index
    struct Arc *next;
    struct Arc *prev;
    // ...
} Arc;
```

When we initialize the `ArcSet` in `createArcSet()`, we assign the pointers
so that each individual cell corresponds to a separate doubly-linked loop
of edges/`Arcs`.

Now, `ArcSet` starts in a state where we have a set of valid doubly-linked loops.
The big idea is, with each edge pair cancellation, to **maintain that valid
state of linked loops**.


For example, if we were to start with two neighboring cells, with two disjoint loops, the `ArcSet` would initially correspond to this picture:

{{< fig src="code/figs/two_cells_before.svg" caption="Initial state of edges for two cells." >}}

After canceling the pair of edges, the `ArcSet` would look like this:

{{< fig src="code/figs/two_cells_after.svg" width="600px" caption="After canceling pairs of edges." >}}

Note that the edges stay in a counter-clockwise loop. But how do we update the
doubly-linked loops?

## Loop surgery

When canceling a symmetric pair of edges `a` and `b`, we splice them out by reconnecting their neighbors.

The edges in the loops are initially chained like:

$$
\begin{aligned}
a^- &\to a \to a^+ \\
b^- &\to b \to b^+
\end{aligned}
$$

which we can also see in the two cell diagram:

{{< fig src="code/figs/two_cells_before_labels.svg" >}}
{{< caption >}}Two loops and the relevant edges before surgery.{{< /caption >}}

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
{{< caption >}}The resulting single loop after surgery.{{< /caption >}}


In the C code, this looks like the following, where `a` and `b` are `Arc` structs:

```c
a->next->prev = b->prev;
a->prev->next = b->next;
b->next->prev = a->prev;
b->prev->next = a->next;
```

Luckily, the loop surgery logic above works in all possible cases and in any order. Consider the examples below. You can check that the linked-loop updating
logic either 1) works in these cases, or 2) doesn't matter, because the pair is
about to be removed anyway.

### Example: four cells

For the first example, we'll consider four cells. Since we've already seen it, we start with two pairs of cells with the common edges removed, and then remove the three remaining pairs one by one:

{{< fig src="code/figs/four_cells_0.svg" >}}
{{< fig src="code/figs/four_cells_1.svg" >}}
{{< fig src="code/figs/four_cells_2.svg" >}}
{{< fig src="code/figs/four_cells_3.svg" >}}

Note that we can **remove edges in any order**. The following is
a completely valid set of two linked-loops (even though the edges in the middle don't enclose any area and will need to be ultimately removed before we form proper polygons):

{{< fig src="code/figs/four_cells_4.svg" >}}

### Example: disk

{{< fig src="code/figs/disk_0.svg" >}}

Removing the edges associated with the center cell leaves a single
ring (with 6 degenerate pairs left to be removed):
{{< fig src="code/figs/disk_1.svg" >}}

{{< fig src="code/figs/disk_2.svg" >}}


### Example: hole

Note that canceling edges might split loops up into separate loops:

{{< fig src="code/figs/ring_0.svg" >}}
{{< fig src="code/figs/ring_1.svg" >}}
{{< fig src="code/figs/ring_2.svg" >}}

Also note that the inner hole of this polygon has the desired clockwise orientation, with the outer loop being counter-clockwise.

## Implementation notes: doubly-linked loops

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), we initialize the edges from cells in `createArcSet()`,
and the `cellToEdgeArcs()` function puts the edges in the proper
order for each cell and connects them in the doubly-linked loop.

In `cancelArcPairs()`, we iterate through the collection of Arcs, find the symmetric pairs with the hash table, remove them, and perform the linked-loop surgery operation.

# Connected components partition loops into polygons

So far we have the outer boundary of our polygons, along with the holes,
and we have the loops of edges in the proper order.

But how do we keep track of which loops (outer and holes) belong to which polygon? Recall the example with three polygons from the top of the page. It has
six loops total, across three polygons. But how can we determine the grouping?

{{< fig src="code/figs/conn_comp_white.svg" width="800px" >}}
{{< caption >}}Six loops, each belonging to one of three polygons. Which loops group together into a polygon?{{< /caption >}}

TODO: polygons are just connected components of cells. so rings that are connected by cells are in the same polygon, even if they're disjoint/separate rings. (even though the rings themselves don't touch)

also note that there is no notion of one polygon being "inside" or "outside" of
another; they're just separate polygons.

The key insight is that **removing a symmetric pair of edges joins their cells' connected components**. We track this with a [union-find data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure): when we cancel an edge pair, we union the components of the two adjacent cells.

Initially, each cell is its own component:

{{< fig src="code/figs/conn_comp_colors_0.svg" width="800px" >}}

As we remove symmetric pairs, components merge:

{{< fig src="code/figs/conn_comp_colors_1.svg" width="800px" >}}
{{< fig src="code/figs/conn_comp_colors_2.svg" width="800px" >}}
{{< fig src="code/figs/conn_comp_colors_3.svg" width="800px" >}}
{{< fig src="code/figs/conn_comp_colors_4.svg" width="800px" >}}

After all symmetric pairs are removed, the remaining components correspond exactly to the polygons we want to output. Loops belonging to the same polygon (both outer and holes) share the same connected component:

{{< fig src="code/figs/conn_comp_colors_5.svg" width="800px" >}}
{{< caption >}}Three connected components, each corresponding to a polygon. The loops within each component form one polygon's outer boundary and holes.{{< /caption >}}

Note that at this stage we know *which* loops belong together, but we don't yet know which loop is the outer boundary versus which are holes. We'll address that in the next section.

## Implementation notes: union-find

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), each `Arc` stores the union-find state directly:

```c
typedef struct Arc {
    H3Index id;

    bool isVisited;
    bool isRemoved;

    // For doubly-linked list of edges in loop
    struct Arc *next;
    struct Arc *prev;

    // For union-find data structure
    struct Arc *parent;
    int64_t rank;
} Arc;
```

The `parent` and `rank` fields implement the [union-find data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure). Two functions handle the core operations:

- `getRoot(Arc *arc)` finds the root of an `Arc`'s connected component, using path compression for efficiency
- `unionArcs(Arc *a, Arc *b)` merges two components using union-by-rank

We identify each connected component by one arbitrary edge ID—specifically, the `id` field of the root `Arc`. When we cancel a symmetric pair of edges in `cancelArcPairs()`, we call `unionArcs()` to merge the components of the two adjacent cells. After all cancellations, loops sharing the same root belong to the same polygon.

# Which loop is "outside"?

(where `parent` is a pointer in a linked list and finds the root. and `rank` is a quantity that is used to keep the tree balanced)

To recap up to this point, we've described how we can eliminate internal edges
to get the polygon boundaries, how we can maintain the orientation of the loops,
and how we keep traack of which loops belong to which polygon.

But how do we determine which loop in a polygon is the outer and which are the holes? What might seem like an easy question is a litte more complicated. Consider the largest polygon from the previous example:

{{< fig src="code/figs/conn_comp_largest.svg" width="800px" >}}

There are four loops of edges here. Eyeballing, it is easy for us to pick out
which one we think *should* be the outer loop---but how do we determine that algorithmically? Let's look at a more extreme example of two loops close to the equator, encircling the entire globe:

{{< globe_map data="data/equator.json" width="500" sync="false" >}}
{{< caption >}}It can be unclear which loop of a polygon is the "correct" outer loop. In this case, the choice is basically arbitrary: we get exactly the same spherical polygon with either choice.{{< /caption >}}

We can assume that we know these two loops are part of the same polygon based on
the connected components calculation, and the orientation of the loops indicates that the interior of the polygon includes the equator (if you're on the surface of the globe, walking along a loop in the direction of the arrows, the interior is to your left---the right-hand rule), so we know that this object is a polygon with one outer loop and one hole. But which one is which?

This is example is designed to make it harder to tell. And, honestly, the right answer is that there is no right answer! Selecting one loop or the other as the outer loop provides just as valid a spherical polygon. This is generally true for all spherical polygons: **you can select any of the loops as the outer with the others as interior, and you maintain a valid spherical polygon that describes exactly the same region**.

However, there's still an obious "correct" answer for smaller polygons (less than a hemisphere), which comes from the interpretation of the polygon if you plotted
it on a flat 2D projection. So while, technically, we can choose any loop to be the outer, we still want to choose the loop that matches this intuition, and
is more likely to work with planar plotting libraries.

Luckily, there's a single rule that picks the "correct" answer for small polygons, and picks a reasonable option for the pathological "global" polygons like the equator example here.

{{< admonition type="note" title="Rule for selecting the outer loop of a polygon" >}}
For each loop in the polygon, compute the (positive, unsigned) area enclosed by the loop, where "enclosed" is defined by the orientation of the loop and the right-hand rule. The outer loop is the one with smallest area; the rest are holes.
{{< /admonition >}}

Let's apply it to the example from above, and see if we get the right answer. We have four loops to compute the area for. Area will be computed in units of
eyeball norm:


<div style="display: grid; grid-template-columns: repeat(2, 1fr); column-gap: 1rem; row-gap: 0; max-width: 800px; margin: 0 auto;">
{{< globe_map data="data/holes_3.json" arrowStep="3" >}}
{{< globe_map data="data/holes_1.json" arrowStep="3" >}}
{{< globe_map data="data/holes_2.json" arrowStep="3" >}}
{{< globe_map data="data/holes_0.json" arrowStep="3" >}}
</div>
{{< caption >}}The loops (dark red), ordered by their enclosed area (light red).
Full polygon (dashed grey) for reference. The orientations of the loops (arrows) cause the first three to enclose most of the globe; the smallest area corresponds to the "natural" outer loop.{{< /caption >}}

We critically depend on the orientation of the loops here.

note that the area calculation depends on "ideal" spherical polgyons (note my post), and all the outputs here will respect that, in particular because no H3 edge is more than 180 degrees, so we can cross the antimeridian or have large loops without problems.

This approach is critically dependent on the area calculation, even for "small" polygons.

In reality, we need to ensure that we are computing the unsigned area.
We might compute a signed area, but let's avoid. Details in this other post.


But also, note that it doesn't matter, technically.

Show a simple globe example

In a polygon, one loop is *special*. The outer loop. the rest are holes.
Actually, not relaly that special. any loop can be the outer loop and still mathematical describe the same polygon, even if it is an unintuitive format.


Note, up to this point, everything has been **discrete**, discrete edges represented as H3 indexes which are integers, graphs and edges. (We've just been doing graph theory, ignorant of the underlying geometry) This is
the first time we need to realize our edges as being embedded in a **continous**
space on the surface of the sphere. And this is where spherical polygons and
a proper area computation come into play. This is what unlocks global polygons.

Ties? who cares! like we said, it doesn't matter which one.

## Implementation notes

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), the outer loop selection happens via sorting. After edge cancellation, we have a set of loops, each tagged with its connected component (the `root` from union-find) and its computed area. The key data structures are:

```c
typedef struct {
    H3Index root;   // connected component identifier
    double area;    // area enclosed by loop (via right-hand rule)
    GeoLoop loop;
} SortableLoop;

typedef struct {
    double outerArea;  // area of outer loop, for sorting polygons
    GeoPolygon poly;
} SortablePoly;
```

The `createSortableLoop()` function computes each loop's area using `geoLoopAreaRads2()`, which returns the (positive, unsigned) area enclosed by following the loop's orientation.

The `createSortableLoopSet()` function collects all loops and sorts them using `cmp_SortableLoop`, which:
1. First sorts by `root` (component ID), grouping loops of the same polygon together
2. Then sorts by `area` (ascending), so the **smallest area comes first**

After sorting, loops from the same polygon are contiguous in memory, with the outer loop (smallest area) first, followed by holes. The `createMultiPolygon()` function walks through this sorted array, grouping consecutive loops with the same `root` into polygons.

# Overview: Algorithm and code

In [uber/h3 #1113](https://github.com/uber/h3/pull/1113), the function `cellsToMultiPolygon()` proceeds through several stages:

1. `validateCellSet`: Check for duplicate cells, which would break edge cancellation logic.
2. `createArcSet`: For each input cell, create `Arc` structs for its 5 or 6 edges. Initialize the hash table for fast edge lookups, create doubly-linked loops of edges, and set up the union-find for keeping track of connected components.
3. `cancelArcPairs`: Loop through all arcs, find symmetric pairs via the hash table, and for each pair:
   - Mark both arcs as removed
   - Perform loop surgery to maintain valid doubly-linked loops
   - Union the connected components of the two adjacent cells
4. `createSortableLoopSet`: Walk the remaining (non-removed) arcs to extract (what we now know to be) boundary loops and translate (discrete) edges to their (continuous) lat/lng coordinates. For each loop, compute its area with `geoLoopAreaRads2()` and record its connected component `root`. Sort all loops by `(component, area)` tuples, so loops of each polygon are contiguous, with smallest-area loop first.
5. `createMultiPolygon`: Walk the sorted loops, grouping consecutive loops with the same root into polygons. The first loop becomes the outer; the rest become holes. Finally, sort polygons by outer loop area (descending) so the largest polygon comes first.

# Performance and improvements

- On large cell sets with many internal edges, this new algorithm is **[roughly 4x faster](https://github.com/uber/h3/pull/1113#issuecomment-3712443984)** than the existing implementation (with additional speedups expected after implementing the Gosper Curve optimization---see below).
- The new algorithm **fixes bugs** that we were running into previously due to floating point comparison issues: [#1048](https://github.com/uber/h3/issues/1048), [#1049](https://github.com/uber/h3/issues/1049), [#1051](https://github.com/uber/h3/issues/1051).
- This algorithm **enables outputting "global" polygons** that, for example, are larger than a hemisphere, cross the antimeridian, or encircle the poles.

# Next up: The Gosper Island

Can we make this even faster?

The algorithm above processes every edge of every input cell. But what if
there were scenarios where we could skip most of that processing?

If a group of cells can be [compacted](https://h3geo.org/docs/highlights/indexing) into a single coarser cell, it is possible to get just the edges of that group
of cells directly, without needing to cancel out the internal edges. This plugs
directly into our existing logic, because, for each compacted cell, we just initialize with this new type of ring of edges.

The fractal shape traced by out by the uncompated children boundary
is called a [Gosper island](https://en.wikipedia.org/wiki/Gosper_curve) or "flowsnake" (as opposed to the [Koch snowflake](https://en.wikipedia.org/wiki/Koch_snowflake)).

This optimization is planned for [uber/h3 #1114](https://github.com/uber/h3/pull/1114) and should provide significant speedups for large, compactible cell sets.
