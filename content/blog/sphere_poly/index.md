---
title: "Elements of Spherical Polygons"
date: 2026-01-09
---

These are some of my notes on constructing spherical polygons, related to
my work on the H3 cells-to-polygon functionality.

When working with spherical polygons, "edge cases" often cause problems: larger-than-a-hemisphere polygons, edges that cross the antimeridian, polygons containing
the north or south pole, or issues with loop orientation.
Luckly, all these issues can be handled easily if you format and interpret polygons
in the right way. This is my take on "the right way".

Start with an image in mind. its Hlepful to have an image in mind as we build up from building blocks.

Rougly, spherical polygon denotes a region on the surface of the unit sphere,
given by an outer ring of points in counter-clockwise order, and zero or more
holes, given by a ring of points in clockwise order.
Of course, there's more detail that we'll go into below.

{{< globe id="three_holes" data="three_holes" arrowStep="3" >}}

You can drag this image (and the others in this post) to see the whole globe.
Click to reset it to whatever I was trying to get you to look at.

# Points

bah radians or degrees 180 deg or $\pi/2$ interchangably.


Latitude/longitude coordinates are treated as elements of an equivalence class induced by the standard spherical embedding into the unit sphere. Two coordinate pairs are equivalent if they map to the same point on the sphere. Canonicalization selects a unique representative within standard bounds.

note this is usually taken care of automatically when you're plugging quantities into
trig functions. but note that if you're testing $x < y$, you're probably doing it wrong. "won't be robust to..."

non-uniqueness can be a feature. if you're exporting to a system that doesn't handle
the sphere natively, you might want to choose representatives that make it easier.
show the example of a box around antimeridian in mapbox vs D3

# Great circle arcs

don't be exactly 180 degrees.
shortest path.
show sweeping a triangle out to 180, and it switches.

we can still acheive this, but we need to add an arc.

# Rings




TODO: good digrammatic polygon with winding order, holes, polys inside polys

What you'll learn:

- what a spherical polygon is
- common formats
- lat/lng/ lng/lat. rads degress
- antimeridian and wrapping
- right hand rule clockwise ordering of points
- why the "outer" loop is kinda arbitrary
- how to surround most of the world in a meter of rope. -- tag
- nothing about any specific format, but what you learn here should generalize.


What you won't learn:

- lat/lng order
- extra vertex repeated at end


Here's a twisted polygon on the globe (drag to rotate, double-click to reset):

{{< globe id="twist" data="twist" rotate="[100, -40, 0]" arrowStep="3" >}}


{{< globe id="ring" data="ring" rotate="[100, -40, 0]" arrowStep="1" >}}


exercise: if i were to give you the equator belt, which one of the two rings is
the outside? how can we decide?
