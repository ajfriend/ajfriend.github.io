# Wicked Fast Spatial Joins with H3

## Parent/child partial ordering

We can define a **partial ordering** on H3 cells according to the parent/child
relationships/containments between cells.

Let $a$ and $b$ be H3 cells. If they are the **same cell**, we'll say $a = b$.

If $a$ is a **child cell** of---or equal to---$b$, we'll say

$$
a \preceq b.
$$

If $a$ is **strictly a child cell** of $b$, we'll say

$$
a \prec b.
$$

If either $a \preceq b$ or $a \succeq b$, we'll say that $a$ and $b$ are **comparable** and write
$$
a \sim b.
$$

If $a \npreceq b$ and $a \nsucceq b$, we'll say that $a$ and $b$ are **incomparable** and write
$$
a \nsim b.
$$

## Total ordering of H3 cells

As integers, consider the lower 52 bit mask of cells.
Cells can be ordered in this way.
We'll call this the "lower 52 ordering".

We'll use the normal inequality symbols when referring to this ordering;
$a < b$ if $a$ comes before $b$ in the lower 52 ordering.

Note that:

- $a \prec b \implies a < b$ 
- $a \preceq b \implies a \leq b$

However, the converse does not hold.
If $a < b$ but $a \nprec b$, we'll use the symbol $a \ll b$.

Thus

- symbol "$<$" defines a **total order** on cells
- symbol "$\prec$" defines a **partial order** on cells

### Which way to order?

Is it better to do natural (ascending) order, or descending order
for the algorithms?

- ascending: children to the left, parents to the right
- descending: parents to the left, children to the right

For the fast compact algo, we want to make sure the process
ends with the elements packed to the left, so that we can
realloc the memory (without having to move all the elements to the front of the array).

### Plotting

would a gantt chart almost be better for plotting parent/child
relationships?

what about a mermaid flow LR flowchart?

### compact algo

- first sort
- in python, first do a iterator to pass through to remove duplicates and children?
    -  iterator might be nice, because it focuses us on the algo instead of the indices (at least figure it out in python first)

### intersection algo

- does it make sense to do the big cells first (instead of alternating left-to-right) because the big cells have a better chance of gobbling up smaller cells.
- doing the small cells can't gobble, but they can cut off things we don't need to inspect
