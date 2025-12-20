---
title: "Areas of Spherical Polygons"
date: 2025-12-15
---

<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

The area of a spherical polygon on a unit sphere is given by the **spherical excess formula**:

$$A = E - (n-2)\pi$$

where $E$ is the sum of the interior angles and $n$ is the number of vertices.

For a spherical triangle with angles $\alpha$, $\beta$, and $\gamma$:

$$A = \alpha + \beta + \gamma - \pi$$

This beautiful result shows that spherical triangles always have angle sums greater than $\pi$ radians, unlike their planar counterparts.

## Interactive Examples

Here's a twisted polygon on the globe (drag to rotate, double-click to reset):

{{< globe id="twist" data="twist" rotate="[100, -40, 0]" >}}

More of this good stuff:

{{< globe id="twist_meridian" data="twist_meridian" rotate="[100, -40, 0]" >}}

A belt around the earth:

{{< globe id="equator" data="equator" rotate="[100, -40, 0]" >}}

A belt and a tie:

{{< globe id="equator_meridian" data="equator_meridian" rotate="[100, -40, 0]" >}}
