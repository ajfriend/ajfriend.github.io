---
title: "H3 Bit Layout"
date: 2026-01-30
---

H3 cells are stored as 64-bit integers, with [bit fields](https://h3geo.org/docs/library/index/cell/) encoding the cell's
mode, resolution, base cell, and hierarchical path.
Below is a diagram of the bit layout for a cell, which can be written in a few ways:

- `'84754a9ffffffff'` (15-digit Python string)
- `0x84754a9ffffffff` (15-digit hex literal)
- `0x084754a9ffffffff` (16-digit hex literal with leading `0`)
- `596538564771053567` (decimal literal)

Note that H3 cells always have a leading `0` in the 16-digit hex representation,
which is usually omitted to bring it down to 15 digits.

In the 15-digit form,
the first digit is always `8` and the second digit is always the cell resolution.
Can you see why that is from the bit layout diagram?


{{< wide-image src="figs/84754a9ffffffff.png" alt="H3 cell bits" >}}


# Sorting H3 cells

Sorting H3 cells as raw integers isn't particularly useful.
Looking at the bit layout, you can see that integer sorting would
group cells by resolution first (since resolution is in the upper bits),
rather than by spatial location.

A more useful ordering is the **lower 52 bit** ordering, which considers only
the lower 52 bits: 7 bits for the base cell plus 3 bits for each of the
15 resolution digits (7 + 3×15 = 52).

This ordering can be implemented by left-shifting 12 bits before comparing:

```c
int cmp_low52(H3Index a, H3Index b) {
    a <<= 12;
    b <<= 12;

    if (a < b) return -1;
    if (a > b) return +1;
    return 0;
}
```

The lower 52 bit ordering has useful properties:

- **Spatial locality**: Cells that are close in space tend to be close in the sort order
- **Hierarchical**: Children always sort before their parents
- **H3_NULL sorts first**: The invalid cell `H3_NULL` (which is `0`) sorts before all valid cells

