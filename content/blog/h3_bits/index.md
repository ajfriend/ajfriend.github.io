---
title: "H3 Bit Layout"
date: 2026-01-30
---

H3 cells are stored as 64-bit integers, with bit groups representing the components
of the cell. Below, we have a diagram of the bit layout for the cell which can be written in a few different variations:

- `'84754a9ffffffff'` (Python string)
- `0x84754a9ffffffff` (hexadecimal literal)
- `0x084754a9ffffffff` (hex literal with leading `0` to bring it to 16 hex digits)
- TODO: `` decimal literal

Note that H3 cells always have a leading `0` in the 16-digit hex representation,
which is usually omitted to bring it down to 15 digits.

In the 15-digit form,
the first digit is always `8` and the second digit is always the cell resolution.
Can you see why that is from the bit layout diagram?


{{< wide-image src="figs/84754a9ffffffff.png" alt="H3 cell bits" >}}


