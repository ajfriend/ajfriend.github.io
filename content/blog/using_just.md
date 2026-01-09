---
title: "Notes on justfiles"
date: 2026-01-09
---

Some notes, mostly for myself, around how I use [`just`](https://github.com/casey/just).


# Clean recipe


```justfile
clean:
    just _rm env
    just _rm .venv
    just _rm '*.pytest_cache'  # put wildcards in quotes
    just _rm .DS_Store

_rm pattern:
    @find . -name "{{pattern}}" -prune -exec rm -rf {} + 2>/dev/null || true
```


# UV

[`uv`](https://docs.astral.sh/uv/) is great, but I really wish it had an "online, but best effort when offline"
for retreiving packages, so that I can work seamlessly when my laptop
doesn't have an internet connection.

As a workaround---since I often run commands through `just`---I can set an
environment variable at the `justfile` level and edit the file when
necessary.


```justfile
export UV_NO_EDITABLE := "1"
export UV_OFFLINE := "0"  # toggle on when offline to avoid failures

test: install
	uv run pytest

@install:
	# uv pip install . does not sync dependencies,
	# and non-editable installs are required for package updates
	uv sync
	uv pip install .
```
