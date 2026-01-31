---
title: "In-Place H3 Cell Compaction"
date: 2026-01-30
draft: true
---

The standard H3 `compactCells` function requires allocating a separate output array.
This post describes an **in-place compaction algorithm** that operates directly on
the input array, requiring only O(1) additional memory beyond the sort.

The algorithm exploits the [lower 52 bit ordering](/blog/h3_bits/#sorting-h3-cells)
to efficiently identify cells that can be compacted.

## Overview

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

Zero values (`H3_NULL`) sort first, which we'll use to our advantage later.

## Phase 2: Canonicalize

After sorting, we remove duplicates and any cells whose ancestors are also
in the array. We walk **right to left**, tracking the current "parent":

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

Why right to left? In the lower 52 bit ordering, parents sort *after* their children.
Walking backwards, we encounter parents first. Any children we then encounter
can be safely removed since their parent represents the same area.

The `is_descendant` check uses the [rich comparison](/blog/h3_bits/#rich-comparison):

```c
bool is_descendant(H3Index child, H3Index parent) {
    int cmp = cmp_canon(child, parent);
    return (cmp == 0) || (cmp == -1);
}
```

## Phase 3: Compact

Now we look for groups of 7 sibling cells (or 6 for pentagons) that can be
replaced by their parent. The key insight is that we can do this in a **single
pass** without re-sorting, by carefully managing which cells are "done" versus
"pending".

### Single-pass compaction

We use three pointers:

- `i`: Everything before `i` is **done** — fully compacted, no future cell can complete a set with them
- `j`: Cells between `i` and `j` are **pending** — they might be part of a set that gets completed (can span multiple resolutions)
- `k`: The cell at `k` is next to **process** — between `j` and `k` is "junk memory" we can ignore and overwrite

```md
| done... | pending... |  junk  | to process... |
          ^            ^        ^
          i            j        k
```

We track the **sequent cell** — the one that would continue or complete the
current sibling set. We only need to look at the top of pending to compute this.

For each cell at `k`:

1. **Resolution 0**: Immediately move to done (no parent to compact into).

2. **Matches sequent**:
   - If it's the last sibling (digit 6, or 5 for pentagons): compact the set,
     put parent at `k`, don't increment `k`.
   - Otherwise: add to pending.

3. **Descendant of sequent**: Add to pending. The descendant will be processed
   first, and might compact up to the level we're waiting for.

4. **Unrelated**: Move pending to done, start fresh with this cell.

```c
// Get the resolution digit (0-6) at the given resolution
int getResDigit(H3Index h, int res);

// Set the resolution digit at the given resolution
H3Index setResDigit(H3Index h, int res, int digit);

// Returns the sequent cell: the cell with the next digit after the input.
H3Index sequent(H3Index cell) {
    int res = getResolution(cell);
    int digit = getResDigit(cell, res);
    return setResDigit(cell, res, digit + 1);
}

int64_t compact_single_pass(H3Index *cells, int64_t n) {
    int64_t i = 0;  // done pointer
    int64_t j = 0;  // pending pointer (end of pending region)
    int64_t k = 0;  // process pointer

    while (k < n) {
        if (cells[k] == 0) {
            k++;
            continue;
        }

        H3Index cur = cells[k];
        int res = getResolution(cur);

        // Resolution 0 cells can't compact — move any pending cells to done
        if (res == 0) {
            cells[j] = cur;
            j++;
            i = j;
            k++;
            continue;
        }

        // Check if cur matches sequent and completes a set
        if (j > i) {
            H3Index seq = sequent(cells[j - 1]);

            if (cur == seq) {
                int digit = getResDigit(cur, res);
                int last_digit = isPentagon(cellToParent(cur, res - 1)) ? 5 : 6;
                if (digit == last_digit) {
                    // Completes the set — compact
                    H3Index parent = cellToParent(cur, res - 1);
                    j -= last_digit;
                    cells[k] = parent;
                    continue;  // Process parent next
                }
                // Otherwise falls through to add to pending
            } else if (cmp_canon(cur, seq) != -1) {
                // Unrelated — pending becomes done
                i = j;
            }
            // If descendant of sequent, falls through
        }

        // At this point, cur is one of:
        // - First cell in a potentially new set (pending was empty)
        // - Sequent that continues but doesn't complete the set
        // - Descendant of the sequent
        // - Unrelated to sequent (pending already moved to done above)
        // Add cur; if digit != 0, can't compact so move to done
        int digit = getResDigit(cur, res);
        cells[j] = cur;
        j++;
        if (digit != 0) {
            i = j;
        }
        k++;
    }

    return j;  // Compacted cells are at positions 0 to j-1
}
```

### Why this works

The lower 52 bit ordering guarantees that siblings are contiguous and children
come before parents. We only need to look at the top of pending to know exactly
which cell would continue or complete the current set.

When a descendant of the sequent arrives, we add it to pending. It will
compact first, potentially producing the cell we were waiting for.

When we compact, the parent goes to `k` and gets processed immediately. If it
completes another set at a coarser resolution, we compact again. Cascading
happens naturally through the main loop.

Resolution 0 cells have no parent, so they skip pending entirely and go
straight to done.

## Complete algorithm

Putting it together:

```c
int64_t compact_inplace(H3Index *cells, int64_t n) {
    // Phase 1: Sort
    qsort(cells, n, sizeof(H3Index), cmp_low52_ptr);

    // Phase 2: Canonicalize
    remove_descendants(cells, n);

    // Phase 3: Compact (single pass)
    // Returns j — the compacted cells are at positions 0 to j-1
    return compact_single_pass(cells, n);
}
```

When processing finishes, the compacted cells are already at the front of the
array (positions `0` to `j-1`). No separate finalization pass is needed.

## Memory usage

- The sort may allocate O(n) or O(log n) memory depending on implementation
- All other operations use O(1) additional memory
- No separate output array needed

## Further reading

- [H3 Bit Layout](/blog/h3_bits/) - Understanding the lower 52 bit ordering
- [PR #552](https://github.com/uber/h3/pull/552) - Canonicalization for H3 cell sets
