---
title: "A Failed Attempt at Improving H3 Compaction"
date: 2026-01-31
toc: true
---

I tried to make the H3 `compactCells` function faster. I failed. But I think
the approach is interesting, and it may still prove useful in the future, so
here's a writeup.

The prototype code is at: https://github.com/ajfriend/h3/pull/1. I used Claude
Code quite a bit for benchmarks, tests, and trying out different sorting algorithms---it did all that much faster than I could have. I still needed
to supply the algorithm, but it did help with cleaning up and combining some
of the logical branches.

# Idea

The motivating idea was that, once we sort a (possibly resolution-heterogeneous) array of H3 cells
using the [lower 52 bit ordering](/blog/h3_bits/#sorting-h3-cells), we can
compact the cells by modifying them in-place in a single pass over the array.

So, while this is true, and the single-pass logic is interesting and maybe
still useful in other contexts, the algorithm's **runtime is
dominated by the sort, and we couldn't get it faster than the existing
hashtable-based implementation**.

That said, this approach isn't a total failure. It does provide a little more structure and functionality than the existing algorithm:

- **Canonical output**: cells end up in a consistent sorted order, useful for
  comparisons and other operations
- **Handles multiple-resolutions, duplicates, and ancestors**: the algorithm gracefully removes redundant cells or partially compacted inputs
- **In-place**: operates directly on the input array with O(1) additional memory
  (beyond the sort)
- **Idempotent**: running it twice produces the same result
- **Fast for sorted input**: if cells are already sorted (common in many
  workflows), this approach *is* faster

The concepts here may still be useful in the future, especially if we are in a situation where our H3 cell sets are often already sorted or mostly sorted.
And, as I mention in [PR #552](https://github.com/uber/h3/pull/552), the
"canonical" ordering we end up with is useful for fast operations on
sets of cells: union, intersection, testing for cell membership, and more.

We document the algorithm here for future consideration.

# Algorithm

The algorithm has three phases:

1. **Sort** by lower 52 bits
2. **Canonicalize**: remove duplicates and descendants
3. **Compact**: merge sibling cells into parents (single pass)

At the end, compacted cells are at the front of the array (`0` to `j-1`).

## Phase 1: Sort

Sort the array using the lower 52 bit comparison:

```c
int cmp_low52(H3Index a, H3Index b) {
    a <<= 12;
    b <<= 12;

    if (a < b) return -1;
    if (a > b) return +1;
    return 0;
}
```

This ordering has a key property: **children always sort before their parents**.
This is because children share the same prefix bits as their parent but have
additional non-`7` digits in the lower bits.

Note that zero values (`H3_NULL`) sort first, which we'll handle later.

## Phase 2: Canonicalize

After sorting, remove duplicates and any cells whose ancestors are also
in the array.

In the lower 52 bit ordering, parents sort *after* their children.
Walking backwards in the array, we encounter parents first.

The algorithm walks **right to left**, keeping track of the current parent cell, and gobbling up any descendants in its shadow:

```c
void remove_descendants(H3Index *cells, int64_t n) {
    H3Index parent = 0;

    for (int64_t i = n - 1; i >= 0; i--) {
        if (cells[i] == 0) {
            continue;
        }

        if (parent == 0) {
            parent = cells[i];
        } else if (is_descendant(cells[i], parent)) {
            cells[i] = 0;  // Remove: ancestor already in array
        } else {
            parent = cells[i];
        }
    }
}
```

The `is_descendant` check can be implemented with a [rich comparison](/blog/h3_bits/#rich-comparison) operator:

```c
bool is_descendant(H3Index child, H3Index parent) {
    int cmp = cmp_canon(child, parent);
    return (cmp == 0) || (cmp == -1);
}
```

## Phase 3: Compact

Now we look for groups of 7 sibling cells (or 6 for pentagons) that can be
replaced by their parent. We can do this in a **single pass** without re-sorting,
by carefully managing which cells are "done" versus "pending". When siblings
compact into a parent, that parent is reprocessed immediately — if it completes
another sibling set at a coarser resolution, compaction cascades up the entire
H3 hierarchy, all within the same pass.

### Single-pass compaction

We use three pointers to work in-place in the array:

- `i`: Everything before `i` is **done** --- fully compacted, no future cell can complete a set with them
- `j`: Cells between `i` and `j` are **pending** --- these are cells that still have a chance to be compacted, depending on what cells are processed next
- `k`: The cell at `k` is next **to be processed** --- between `j` and `k` is "junk memory" we can ignore and overwrite

The `i,j,k` all start at `0`. At the end, `k == n` (all cells processed) and `i == j`, with the compacted cells in positions `0` to `j-1`.

Here's a diagram of the working set:

```md
| done | pending |  junk  | to process |
^      ^         ^        ^            ^
0      i         j        k            n
```

During the algorithm, we compute the **next sibling** of the pending set: the cell that would continue or complete the
current sibling set. We only need to look at the top of the pending stack to compute this. We compare the next sibling with the next cell to process at `cells[k]`.

Before we get into the main compaction logic, let's define some helper functions:

```c
// Helper: get immediate parent (one resolution coarser)
H3Index parent(H3Index cell) {
    return cellToParent(cell, getResolution(cell) - 1);
}

// Helper: number of children (6 for pentagons, 7 for hexagons)
int num_children(H3Index cell) {
    return isPentagon(cell) ? 6 : 7;
}

// The next sibling (cell with next digit). Skips digit 1 for pentagons.
H3Index next_sibling(H3Index cell) {
    int res = getResolution(cell);
    int next = getResDigit(cell, res) + 1;

    if (next == 1 && isPentagon(parent(cell))) {
        next = 2;
    }

    return setResDigit(cell, res, next);
}

// Can this cell start a compactable sibling set? (res >= 1, digit 0)
bool is_first_child(H3Index cell) {
    int res = getResolution(cell);
    return res >= 1 && getResDigit(cell, res) == 0;
}

// Is this cell the last sibling? (digit 6)
bool is_last_child(H3Index cell) {
    int res = getResolution(cell);
    return getResDigit(cell, res) == 6;
}

// Is cur the first descendant of target? (descendant with all-zero path)
bool is_first_descendant_of(H3Index cur, H3Index target) {
    if (cmp_canon(cur, target) != -1) return false;

    int target_res = getResolution(target);
    int cur_res = getResolution(cur);
    for (int r = target_res + 1; r <= cur_res; r++) {
        if (getResDigit(cur, r) != 0) return false;
    }
    return true;
}
```

With the helpers defined, the main loop handles each cell (skipping nulls)
with two branches:

**If pending is non-empty**, compute the next sibling `sib` from the top of pending (`cells[j-1]`)
and compare with `cur = cells[k]` (the next incoming cell to process):
- **`cur` matches `sib`**: Add to pending. If it's the last sibling (digit 6), compact the
  set, put parent back at `cells[k]`, and reprocess without incrementing `k`.
- **`cur` is a "first descendant" of `sib`**: Add to pending. It might compact up to the `sib` we're waiting for.
- **Otherwise**: Flush pending cells to done, since they can't be compacted further. Fall through to empty case below to see if `cur` can start a new sibling set.

**If pending is empty** (or we just flushed), the cell either starts a new
potential sibling set or goes straight to done. If it's a "first child"
(res ≥ 1 and digit 0), add to pending. Otherwise, flush immediately.

```c
int64_t compact_single_pass(H3Index *cells, int64_t n) {
    int64_t i = 0;  // end of "done"
    int64_t j = 0;  // end of "pending"
    int64_t k = 0;  // next to process

    while (k < n) {
        H3Index cur = cells[k];

        // Skip over 0 (H3_NULL) values
        if (cur == 0) {
            k++;
            continue;
        }

        // Try to extend pending set
        if (i < j) {
            H3Index sib = next_sibling(cells[j - 1]);
            if (cur == sib) {
                cells[j++] = cur;  // Add to pending.
                if (is_last_child(cur)) {
                    // Compact siblings, replace with parent
                    H3Index p = parent(cur);
                    cells[k] = p;          // Put parent as next "to process".
                    j -= num_children(p);  // Clear these children from pending.
                } else {
                    // Middle sibling, move along.
                    k++;
                }
                continue;
            } else if (is_first_descendant_of(cur, sib)) {
                cells[j++] = cur;  // Add to pending.
                k++;
                continue;
            } else {
                // `cur` is not the next sibling or descendant of.
                i = j;  // Flush the pending stack.
                // Consider `cur` below.
            }
        }

        // If here, pending stack is empty.
        // Start new potential sibling set.
        cells[j++] = cur;
        // If not a first child, flush immediately.
        if (!is_first_child(cur)) i = j;
        k++;
    }

    return j;
}
```

### Why this works

The lower 52 bit ordering guarantees that siblings are contiguous and children
come before parents. We only need to look at the top of pending to know exactly
which cell would continue or complete the current set.

When a first descendant of the next sibling arrives, we add it to pending. It will
compact first, potentially producing the cell we were waiting for.

When we compact, the parent goes to `k` and gets reprocessed immediately. If it
completes another set at a coarser resolution, we compact again. Cascading
happens naturally through the main loop.

Cells that can't start a compactable set---resolution 0 (no parent) or
digit ≠ 0 (missing earlier siblings)---go straight to done via `is_first_child`.

## Complete algorithm

Putting it together:

```c
int64_t compact_inplace(H3Index *cells, int64_t n) {
    // Phase 1: Sort
    qsort(cells, n, sizeof(H3Index), cmp_low52_ptr);

    // Phase 2: Canonicalize
    remove_descendants(cells, n);

    // Phase 3: Compact (single pass)
    // Returns j. The compacted cells are at positions 0 to j-1
    return compact_single_pass(cells, n);
}
```

When processing finishes, the compacted cells are at the front of the
array in positions `0` to `j-1`.

## Memory usage

- The sort may allocate O(n) or O(log n) memory depending on implementation
- All other operations use O(1) additional memory
- No separate output array needed

# Performance

## Why it's slower

Profiling showed that up to **95% of the runtime is spent in sorting** for large, unsorted inputs
like polygon fills. The actual compaction logic is fast, but we can't beat the
existing hash-table approach because:

- Hash tables are O(n) average case
- Sorting is O(n log n)
- Even a highly optimized custom sort couldn't close the gap

## Sorting strategies

We tried several sorting strategies:

| Approach | Result |
|----------|--------|
| `qsort()` (libc) | Baseline, function pointer overhead |
| Custom quicksort | ~32% faster than qsort (inlined comparison) |
| Timsort | Rejected — exploits sorted "runs", but real data had avg run length of 2.4 (no structure to exploit) |
| Adaptive sort | Best compromise — checks sortedness first, uses insertion sort if ≤1% inversions |

## Benchmarks

Benchmarks on an Apple M3 laptop, using the adaptive sort implementation. Take with a grain of salt (they're LLM generated), but they illustrate the tradeoffs:

| Test Case | `compactCells` (hash) | `compactCellsInPlace` (sort) | Winner |
|-----------|----------------------|------------------------------|--------|
| Small disk (37 cells) | 0.32 µs | 0.22 µs | **In-place** |
| Medium disk (271 cells) | 1.81 µs | 2.24 µs | Hash |
| Large disk (1261 cells) | 8.47 µs | 11.95 µs | Hash |
| Base cell children (2401 cells) | 14.11 µs | 11.99 µs | **In-place** |
| Sparse cells (100 cells) | 0.79 µs | 0.70 µs | **In-place** |
| Pentagon children (286 cells) | 1.93 µs | 1.49 µs | **In-place** |
| Colorado polygon (47823 cells) | 378 µs | 2053 µs | Hash |

In-place wins when the data is already sorted (e.g., from `cellToChildren`)
or very small. It loses on large unsorted inputs like polygon fills (~5x slower on Colorado). **Note, however, that future versions of the polygon-to-cells functions
in H3 may provide sorted outputs---so the sorted scenario won't be uncommon.**

# Further reading

- [H3 Bit Layout](/blog/h3_bits/) --- "Lower 52 bit" ordering for H3 cells
- [PR #552](https://github.com/uber/h3/pull/552) --- An older PR of mine around
ordering/canonicalizing sets of H3 cells.
- Prototype code: https://github.com/ajfriend/h3/pull/1
