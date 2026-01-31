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

For each cell at `k`, we first check if the stack is empty:

**Empty stack**: If the cell is a "first child" (res ≥ 1 and digit 0 at its
resolution), it could start a compactable set — add to pending. Otherwise
(res 0, or digit ≠ 0), it can't compact — move straight to done.

**Non-empty stack**: Compute the sequent from the top of pending, then:

1. **Matches sequent**: Add to stack. If it's the last sibling (digit 6),
   compact the set, put parent at `k`, and reprocess without incrementing `k`.

2. **First descendant of sequent**: Add to stack. It might compact up to
   the level we're waiting for.

3. **Unrelated**: Flush pending to done. Don't increment `k` — reconsider
   this cell with an empty stack on the next iteration.

```c
// Get the resolution digit (0-6) at the given resolution
int getResDigit(H3Index h, int res);

// Set the resolution digit at the given resolution
H3Index setResDigit(H3Index h, int res, int digit);

// Returns the sequent cell: the cell with the next digit after the input.
H3Index sequent(H3Index cell) {
    int res = getResolution(cell);
    int digit = getResDigit(cell, res);
    int next_digit = digit + 1;

    // Pentagon cells skip digit 1
    if (next_digit == 1 && isPentagon(cellToParent(cell, res - 1))) {
        next_digit = 2;
    }

    return setResDigit(cell, res, next_digit);
}

// Returns true if cell has res >= 1 and its res digit is 0.
bool is_first_child(H3Index cell) {
    int res = getResolution(cell);
    return res >= 1 && getResDigit(cell, res) == 0;
}

// Returns true if cur is a first descendant of seq:
// - cur is a proper descendant of seq (finer resolution, same ancestor path)
// - all digits between seq's res and cur's res are 0
bool is_first_descendant_of(H3Index cur, H3Index seq) {
    if (cmp_canon(cur, seq) != -1) return false;

    int seq_res = getResolution(seq);
    int cur_res = getResolution(cur);
    for (int r = seq_res + 1; r <= cur_res; r++) {
        if (getResDigit(cur, r) != 0) return false;
    }
    return true;
}

int64_t compact_single_pass(H3Index *cells, int64_t n) {
    int64_t i = 0;  // done pointer
    int64_t j = 0;  // pending pointer (end of pending region)
    int64_t k = 0;  // process pointer

    // Invariants:
    // - 0 <= i <= j <= k <= n
    // - cells[0..i) are done (fully compacted)
    // - cells[i..j) are pending (might compact with future cells)
    // - cells[j..k) are junk (can be overwritten)
    // - cells[k..n) are yet to be processed
    while (k < n) {
        if (cells[k] == 0) {
            k++;
            continue;
        }

        H3Index cur = cells[k];

        // Empty stack: cur either starts a new pending set or goes to done
        if (i == j) {
            cells[j] = cur;
            j++;
            if (!is_first_child(cur)) {
                i = j;  // Can't compact, move to done
            }
            k++;
            continue;
        }

        // Non-empty stack: check if cur continues or completes the set
        H3Index seq = sequent(cells[j - 1]);

        if (cur == seq) {
            // Continues or completes the set — add to stack
            cells[j] = cur;
            j++;

            int res = getResolution(cur);
            int digit = getResDigit(cur, res);
            H3Index parent = cellToParent(cur, res - 1);
            if (digit == 6) {
                // Completes the set — compact
                int num_children = isPentagon(parent) ? 6 : 7;
                j -= num_children;
                cells[k] = parent;
                continue;  // Process parent next
            }
            k++;
            continue;
        }

        if (is_first_descendant_of(cur, seq)) {
            // First descendant of sequent — add to stack
            cells[j] = cur;
            j++;
            k++;
            continue;
        }

        // Unrelated (or non-first descendant) — flush stack, reconsider cur
        i = j;
    }

    return j;  // Compacted cells are at positions 0 to j-1
}
```

### Why this works

The lower 52 bit ordering guarantees that siblings are contiguous and children
come before parents. We only need to look at the top of pending to know exactly
which cell would continue or complete the current set.

When a first descendant of the sequent arrives, we add it to pending. It will
compact first, potentially producing the cell we were waiting for.

When we compact, the parent goes to `k` and gets processed immediately. If it
completes another set at a coarser resolution, we compact again. Cascading
happens naturally through the main loop.

Cells that can't start a compactable set — resolution 0 (no parent) or
digit ≠ 0 (missing earlier siblings) — go straight to done via `is_first_child`.

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
