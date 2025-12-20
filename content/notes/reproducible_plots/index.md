---
title: "Reproducible Plots Example"
date: 2025-12-15
---

This post demonstrates keeping Python code and generated figures together with the post content.

## Sine and Cosine Waves

Here's a simple plot of sine and cosine functions generated with matplotlib:

![Sine and Cosine](images/trig_functions.png)

## Random Walk

A visualization of a 2D random walk with 1000 steps:

![Random Walk](images/random_walk.png)

## Regenerating the Figures

All figures in this post are generated from Python code in the `code/` directory. The project uses [uv](https://docs.astral.sh/uv/) to manage dependencies, ensuring reproducibility across different environments and Python versions.

To regenerate the figures:

```bash
cd content/blog/reproducible_plots
just generate
```

The Python scripts, dependencies (`pyproject.toml` and `uv.lock`), and justfile are all kept in the same folder as this post, making the analysis fully reproducible.
