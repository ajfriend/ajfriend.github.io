---
title: "[WIP] Making H3's cells-to-polygon faster"
date: 2026-01-09
---

This post is currently a quick-and-dirty attempt at explaining the algorithm
behind [cellsToMultiPolygon core algorithm #1113 · uber/h3](https://github.com/uber/h3/pull/1113). Since I think the algorithm is pretty cool, I'll try to grow this into a
proper blog post with more context, background, etc.


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


In the C code, this looks like:

```c
a->next->prev = b->prev;
a->prev->next = b->next;
b->next->prev = a->prev;
b->prev->next = a->next;
```

## Other edge cancellation examples

Luckily, the loop surgery logic above works in all possible cases.






# Connected components partition loops into polygons

# Which loop is "outside"?



# OLD BELOW

# Intro

This article covers recent improvements in H3's algorithms to
convert H3 cells to polygons (like a GeoJSON multipolygon), where
we fix some bugs, unlock "global" polygons, and run 4x faster.

- what's h3. quick intro on H3. cells. maybe not even edges yet.
- whats the output? format?

Image of what I'm talking about. probably california to california.

bits that matter:

- regions are laid out with loops of lat/lng points. loops are in counter-clockwise order
- holes are opposite
- can have multiple polygons within each other.

In a polygon, one loop is *special*. The outer loop. the rest are holes.
Actually, not relaly that special. any loop can be the outer loop and still mathematical describe the same polygon, even if it is an unintuitive format.


a tricky one might look like: blah

OK. let's get to it. let's do it one cell at a time...

(ed. when do i introduce linked list?) "I'll be using edges. sequence of edges. list to keep track of order. linked list"

# A single cell

could just call boundary.
but we can also get edges.
we could match up which edge goes to which, but it turns out
we can output these in order for any cell

maybe this is when we demonstrate first edge digram. inside cell.

# Two cells

every edge has a reverse. we can see that with two neighboring cells.

compute the reverse. look for collisions.
ok, but this just gives us the bag of edges.
how do we get a loop in order?

we can go back to the idea of trying to figure out which one is which.

but what if we can exploit the fact that these edges are already sorted
in each cell. (ed: how do we demonstrate the loop?)

# Four cells

so we've done two edge pair removals.

show the thing isn't degenerate.

we can even have a floating thing in the middle. that's fine.

# cells in a C. then add a new cell to get one missing in the middle


# summary

- this works in general. get holes. nested
- however, we just have loops. no polygons.
- notes on implementation.
	- some dictionary
	- the doubly linked list for the loops


- which loops belong to which polygons? which loops are outer and which are holes?





