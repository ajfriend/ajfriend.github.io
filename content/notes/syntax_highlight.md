---
title: "Syntax Highlighting Demo"
date: 2025-12-15
---

Testing code syntax highlighting with different languages.

## Python

```python
def fibonacci(n):
    """Generate Fibonacci sequence up to n terms."""
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Generate first 10 Fibonacci numbers
print(fibonacci(10))
```

## C

```c
#include <stdio.h>
#include <stdlib.h>

/* Calculate factorial recursively */
unsigned long factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main(void) {
    int num = 10;
    printf("Factorial of %d is %lu\n", num, factorial(num));
    return 0;
}
```

Both examples show functions with recursion or iteration.

## Footnotes

Markdown supports footnotes[^1] for adding references or additional context without cluttering the main text. You can also use named footnotes[^python-note] for better organization.

Multiple references to the same footnote work too[^1].

[^1]: This is a simple footnote with an auto-numbered reference.
[^python-note]: The Python Fibonacci implementation uses iteration rather than recursion for better performance with large values of n.
