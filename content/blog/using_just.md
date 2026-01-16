---
title: "Notes on justfiles"
date: 2026-01-01
---

Some notes---mostly for myself---around how I use [`just`](https://github.com/casey/just).


# Clean recipe


```justfile
clean:
    just _rm env
    just _rm .venv
    just _rm '*.pytest_cache'  # put wildcards in quotes
    just _rm .DS_Store

_rm pattern:
    -@find . -name "{{pattern}}" -prune -exec rm -rf {} +
```

Alternatively, there's `git clean -fdx`, but I don't use that often.


# UV

[`uv`](https://docs.astral.sh/uv/) is great, but I really wish it had an "online, but best effort when offline"
for retrieving packages, so that I can work seamlessly when my laptop
doesn't have an internet connection.

As a workaround---since I run most commands through `just`---I can set an
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

# list commands and groups

A default rule for listing the recipes:

```justfile
_:
	just --list
```

Can control that output by defining groups. Comments immediately before show
up in `just --list` output.

```justfile
[group('extra')]
lab:
	uv run jupyter lab

# remove env and lockfile
[group('clean')]
purge: clean
	-rm uv.lock
```

# just test as `t`

I have the following in my `~/.zshrc`:

```bash
alias t='just test'
```

Across projects and programming languages, I often have a `just test` command
that, well, tests whatever it is I'm currently working on. When I'm working on
the H3 C repo, it'll usually look something like this:

```justfile
test: build
    # ./build/bin/testH3CellAreaExhaustive
    # ./build/bin/testEdgeCellsToPoly
    # ./build/bin/testDirectedEdge
    # ./build/bin/testArea
    # just test-slow
    just test-fast
    # ./build/bin/testCellsToMultiPoly
```

The alias to `t` makes it so I can just type a single character in my terminal
to test, which is probably the command I'm running most often.

The `justfile`
gives me some flexibility: I might be changing one function and so want to run
a specific test, or I might want to run the whole test suite, or some specific
benchmark.

Editing the `justfile` (and commenting out things that I might switch back to in the near future) gives me a nice combination of speed/convenience, along
with the flexibility to have that `t` do different things at different times.

