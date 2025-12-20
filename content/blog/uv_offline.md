---
title: "Using uv Offline"
date: 2025-12-17
---

Using Python's `uv` package manager in offline environments.

## Overview

`uv` is a fast Python package installer and resolver written in Rust. Working offline requires pre-downloading dependencies.

## Setting Up Offline Cache

First, download packages while online:

```bash
# Download packages to cache
uv pip sync requirements.txt --cache-dir ./uv-cache
```

## Using Cached Packages

When offline, point to your local cache:

```bash
# Install from cache without network access
uv pip install --cache-dir ./uv-cache --offline package-name
```

## Best Practices

- Maintain a local package index
- Pre-download all dependencies for your project
- Use `--offline` flag to ensure no network requests
- Keep cache synchronized with requirements

## Example Workflow

```bash
# Online: prepare cache
uv pip sync requirements.txt --cache-dir ./uv-cache

# Offline: install from cache
uv pip install --cache-dir ./uv-cache --offline -r requirements.txt
```
