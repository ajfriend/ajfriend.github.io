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

(Nod to other formats? GeoJSON. State that this will be agnostic.) List some other formats. Maybe.

{{< globe data="ring" arrowStep="1" >}}

A polygon with one outer ring (counter-clockwise) and one hole (clockwise).

You can drag the image (and others in this post) to see different parts of the globe.
Double click to reset the image to whatever I was trying to get you to look at.

# Spherical model of Earth

In this post, we'll assume the polygons are on the surface of the unit sphere.
While it's true the Earth is roughly a sphere, it's
[better approximated by an ellipsoid](https://en.wikipedia.org/wiki/Earth_ellipsoid).
We'll use the sphere model because that's what H3 uses.

To compute surface areas on the Earth, you'd scale up any areas from the unit
sphere by $R^2$, where $R \approx 6{,}371\ \text{km}$.

# Points

We'll describe points on the sphere as the latitude–longitude pair
$(\theta, \phi)$, in units of degrees. Typically, you'll see the values
normalized like
\[
\begin{aligned}
-90   &\le \theta \le +90, \\
-180  &<  \phi   \le +180,
\end{aligned}
\tag{1}
\]

but this shouldn't be strictly necessary, as I'll argue below.

## What doesn't matter

There are many other conventions and notations.
Almost everything described here is unchanged if you instead use
longitude–latitude order, radians instead of degrees,
write “lon” instead of “lng”, or use different symbols
(I like $\theta$ and $\phi$ because the little lines go through the little circles mnemonically).

I might say either 180 degrees or $\frac{\pi}{2}$, meaning the same thing.

## What *does* matter

"one approach is to try and make it unique, like..." but even that doesn't work!
Note that the representation above is not unique; a single point can correspond
to many different $(\theta, \phi)$ pairs.
You'll often see mention of bounds like in Eq. (1) to make the representation
unique, but event that doesn't quite do it:
the north pole can be represented equivalently as
$(90, 0)$ or $(90, 10)$ or $(90, 123456789)$, since the longitude value can
be anything.

So, instead of trying to make things unique, let's allow it to be anything.
That is, our algorithms should be equivalent for any representations of the same
points, and shouldn't depend on antyhing from the representation outside
of which point on the sphere it represents.


Another way to say this is via an equivalance class.
We consider all $(\theta, \phi)$ points the same if they map to the same point
on the sphere in 3D, that is:

\[
f(\theta, \phi) =
\begin{bmatrix}
\cos\theta \cos\phi \\
\cos\theta \sin\phi \\
\sin\theta
\end{bmatrix}.
\]

You don't have to actually do that transformation. You just need to make sure
your code respects the equivalence class.


Note that this definition is nice because it handles all cases:

- $f(90, x) = f(90, y)$ for any $x, y$
- $f(\theta, \phi) = f(\theta, \phi + 360)$

And we can even extend $\theta$ outside its normal bounds. For example
$(80, 0)$ can also be written $(110, 180)$. (Does this need an image?)


Note that, luckily, this is usually taken care of automatically when you're plugging quantities into trig functions. but note that if you're testing $x < y$, you're probably doing it wrong. "won't be robust to..."

non-uniqueness can be a feature. if you're exporting to a system that doesn't handle
the sphere natively, you might want to choose representatives that make it easier.
show the example of a box around antimeridian in mapbox vs D3

## Bottom line (ugh..)

Lat/lng points should be treated as represenatives of a point on 3D sphere,
and algorithms, plots, everything we do should work and look the same
no matter what representation you give them.

# Great circle arcs

(
TODO: color the lune in light grey. draw the arc on the orthographic.
The ortho and mercator should match exactly.
color the points red and green. color the lune lines accordingly.
)

The great circle arc between `(0, -150)` and `(0,0)` goes east:

{{< globe_arc points="[(0, -150), (0, 0)]" strokeWidth="5" projection="equirectangular"  width="1000" >}}

This is because its the shortest path, look at this lune:

{{< globe_poly points="[(90, 0), (0, -150), (-90, 0), (0, 0)]" rotate="[90, 0, 180]" >}}

Now, if we extend the endpoint further east to `(0, 60)`, we see that the arc takes the opposite path around the globe:

{{< globe_arc points="[(0, -150), (0, 60)]" strokeWidth="5" projection="equirectangular"  width="1000" >}}

Checking the lune confirms it is the shortest path:

{{< globe_poly points="[(90, 0), (0, 60), (-90, 0), (0, -150)]" rotate="[90, 0, 180]" >}}

Alternatively, if we had continued in the other direction, the path would have been
more than 180 degrees:

{{< globe_poly points="[(90, 0), (0, -150), (-90, 0), (0, 60)]" rotate="[90, 0, 180]" >}}

But it is possible to represent that path, we just need to add an intermediate
point to break up the any arcs that would otherwise be $\geq 180$ degrees:

{{< globe_arc points="[(0, -150), (0, 0), (0, 60)]" strokeWidth="5" projection="equirectangular"  width="1000" >}}


{{< globe_arc points="[(0, 0), (0, 120), (0, 270)]" strokeWidth="10" >}}

{{< globe_arc points="[(0, 0), (45, 90), (30, 120), (60, 150)]" rotate="[20, 45, 0]" >}}

don't be exactly 180 degrees.
shortest path.
show sweeping a triangle out to 180, and it switches.

{{< globe_poly points="[(90, 0), (0, 0), (0, 90)]" arrowStep="1"  >}}

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

{{< globe data="twist" rotate="[40, 50, 0]" arrowStep="3" >}}


{{< globe data="ring" arrowStep="1" >}}


exercise: if i were to give you the equator belt, which one of the two rings is
the outside? how can we decide?

# Composing multiple elements

You can combine different styled features (polygons, lines, points) in a single map using the `globe_map` shortcode with a GeoJSON FeatureCollection.

Here's the same data shown on an orthographic projection (globe):

{{< globe_map data="composed_example" >}}

And on an equirectangular projection (flat map):

{{< globe_map data="composed_example" projection="equirectangular" width="1000" >}}
