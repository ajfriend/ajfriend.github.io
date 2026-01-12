---
title: "Elements of Spherical Polygons"
date: 2026-01-09
---

These are some of my notes on constructing and working with spherical polygons,
based off my work on H3.


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
