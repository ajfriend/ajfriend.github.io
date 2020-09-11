# Configuration for MkDocs with the Material theme

```python
import tensorflow as tf

def foo():
    print('hello')
```

## SmartyPants punctuation

- https://python-markdown.github.io/extensions/
- https://python-markdown.github.io/extensions/smarty/

For en-dash, (--), em-dash (---), and ellipsis (...).

```yaml
markdown_extensions:
  - smarty
```

## Math

Inline and block math: $\sum_{i=1}^N x^i$

$$
\sum_{i=1}^N x^i
$$

```yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true

extra_javascript:
  - javascripts/config.js
  - https://polyfill.io/v3/polyfill.min.js?features=es6
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

## Helpful sites

- https://python-markdown.github.io/extensions/
- http://madrus4u.com/mdocs/engine/styling/
- https://code.kx.com/q/about/sg/ 
- https://facelessuser.github.io/pymdown-extensions/
