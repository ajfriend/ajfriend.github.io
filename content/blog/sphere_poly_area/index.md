---
title: "[WIP] Computing Spherical Polygon Areas"
date: 2026-01-03
---

<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>

The [H3](https://github.com/uber/h3/) library provides a hexagonal
geospatial grid system, and being a geospatial library, one of the things
we want to be able to do is to compute the surface areas of polygons on
the sphere. This post will go through the math behind the spherical polygon area
calculation that we use, which I mostly learned about through the [D3 library's area calculation code](https://github.com/d3/d3-geo/blob/main/src/area.js).

This algorithm is robust enough to handle many tricky polygons, including ones
that may be larger than a hemisphere, contain the north or south pole, or cross
the antimeridian. Drag around the plot below to see an example:

{{< globe id="twist" data="twist" rotate="[100, -40, 0]" >}}

One approach is to break these up. We don't want to do that. We want to be able
to handle these tricky polygons naturally.
Q: Can geopandas compute the area here?

What do I mean by tricky? i mean, geojson.io can't even plot it.
Give the users a link to a geojson file of the full polygon.

ideally, we'd like H3 to be globe native


# Polygons on a sphere

# Area of a spherical triangle

The surface area for a polygon on

There are several formulas for the E (also known as area when the unit sphere),
the one that we'll be using is from.

We start with the formula for the area of a spherical triangle given in
Todhunter's Spherical Trigonomotry[^todhunter]:

[^todhunter]: Todhunter, Spherical Trigonomotry (1871), Sec. 103, Eq. (2). On page number 74 in https://www.gutenberg.org/files/19770/19770-pdf.pdf

$$
\tan \frac{E}{2} =
\frac{
  \sin \frac{a}{2}\,\sin \frac{b}{2}\,\sin C
}{
  \cos \frac{a}{2}\,\cos \frac{b}{2}
  +
  \sin \frac{a}{2}\,\sin \frac{b}{2}\,\cos C
}
$$

<p style="text-align: center;">
  <img src="code/figs/triangle.png" alt="Spherical triangle" style="max-width: 400px; width: 100%; height: auto;">
</p>

Here, $a$ and $b$ are the arc lengths of two sides of the spherical triangle (measured in radians on the unit sphere), and $C$ is the angle between them. $E$ is the spherical excess, which is equal to the surface area of the triangle on the unit sphere.



# Special case: polar triangle

To compute the area of a polygon, we sum the signed areas of triangles formed by each edge and a reference point. Using the south pole as the reference point simplifies the math. Counter-clockwise triangles contribute positive area (red), clockwise triangles contribute negative area (blue). Where they overlap, the areas cancel out, leaving only the polygon's interior.

{{< globe_triangles data="data/hexagon_na.json" rotate="[-60, -40, 0]" >}}
{{< caption >}}A hexagon near the tip of South America. Each edge forms a triangle with the south pole. Red triangles (CCW) add area; blue triangles (CW) subtract. The net sum gives the polygon's area.{{< /caption >}}

We can form a special case where the point $C$ is the south pole, so
$(\text{lat}_c, \text{lng}_c) = (\phi_c, \theta_c) = \left(-\frac{\pi}{2}, 0 \right)$.

The angle at $C$ is just the difference between the longitudes:
$C = \theta_b - \theta_a$.
The arc length given by $a$ is formed based on the distance to the south pole, so
$a = \phi_a - (-\frac{\pi}{2}) = \phi_a + \frac{\pi}{2}$. The same for $b = \phi_b + \frac{\pi}{2}$.

Plugging these in, we get

$$
\tan \frac{E}{2} =
\frac{
  \sin(\frac{\phi_a}{2} + \frac{\pi}{4}) \sin(\frac{\phi_b}{2} + \frac{\pi}{4}) \sin(\theta_b - \theta_a)
}{
  \cos(\frac{\phi_a}{2} + \frac{\pi}{4}) \cos(\frac{\phi_b}{2} + \frac{\pi}{4})
  +
  \sin(\frac{\phi_a}{2} + \frac{\pi}{4}) \sin(\frac{\phi_b}{2} + \frac{\pi}{4}) \cos(\theta_b - \theta_a)
}
$$

or, letting $\phi'_x = \frac{\phi_x}{2} + \frac{\pi}{4}$:

$$
\tan \frac{E}{2} =
\frac{
  \sin(\phi'_a) \sin(\phi'_b) \sin(\theta_b - \theta_a)
}{
  \cos(\phi'_a) \cos(\phi'_b)
  +
  \sin(\phi'_a) \sin(\phi'_b) \cos(\theta_b - \theta_a)
}
$$



# arctangent

To extract $E$ from this formula computationally, we use the two-argument $\text{atan2}$ function to handle quadrants and division by zero properly:

$$
E = 2 \cdot \text{atan2}\left(
  \sin \frac{a}{2}\,\sin \frac{b}{2}\,\sin C,\,
  \cos \frac{a}{2}\,\cos \frac{b}{2} + \sin \frac{a}{2}\,\sin \frac{b}{2}\,\cos C
\right)
$$


# References

[geometry - Deriving the Surface Area of a Spherical Triangle - Mathematics Stack Exchange](https://math.stackexchange.com/questions/110075/deriving-the-surface-area-of-a-spherical-triangle)

