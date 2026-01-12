---
title: "Making H3's cells-to-polygon faster"
date: 2026-01-09
---

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





