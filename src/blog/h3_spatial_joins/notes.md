# big ideas

- H3 ~= Hilbert curve?
    + eh, people will want to see that
- transform spatial problem with weird data formats into a standard CS problem, ordered searching and sorting
- summarize collections of hexes by their **bounding** hexes
    + that lets you skip lots of computation
- you have to work in the H3 space
    + translate everything there, and operations become fast
    + accept the geo accuracy tradeoffs
- compression as the default for storage/computation!

## coding ideas

- use C cell child iterator object to put on the stack to know what thing to expect next
    + remaining question: what's the easiest way to flush out the cells we've already seen?
    + ooooh! can i write a `backstep` function? bidirectional iterator!
    
    
## 2021-01-10

oh shit! we don't even need a separate stack! just use the first part of the input array.
you'll never need more space than the input you've read so far!

use i,j,k pointers to keep track of:

i: stack start
j: stack end
k: next input

this makes "flusing" the stack free!

