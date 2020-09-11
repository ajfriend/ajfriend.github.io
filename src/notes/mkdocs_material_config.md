# MkDocs/Material config

## Admonitions

https://squidfunk.github.io/mkdocs-material/reference/admonitions/

!!! note
    You can make admonition blocks!

!!! warning
    They're super fun.

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - admonition
      - pymdownx.details
      - pymdownx.superfences
    ```

## Content tabs

https://squidfunk.github.io/mkdocs-material/reference/content-tabs/

=== "Python 3"

    ```python
    for i in range(10):
        print(x)
    ```

=== "Python 2"

    ```python
    for i in xrange(10):
        print x
    ```


??? tldr "Config"
    ```yaml
    markdown_extensions:
      - pymdownx.tabbed
      - pymdownx.superfences
    ```

## Code highlighting

```python
import h3.api.numpy_int as h3

def foo():
    print('hello')
```

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - codehilite
    ```

## SmartyPants punctuation

- https://python-markdown.github.io/extensions/
- https://python-markdown.github.io/extensions/smarty/

For en-dash, (--), em-dash (---), and ellipsis (...).

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - smarty
    ```

## Math

Inline and block math: $\sum_{i=1}^N x^i$

$$
\sum_{i=1}^N x^i
$$

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - pymdownx.arithmatex:
          generic: true

    extra_javascript:
      - javascripts/config.js
      - https://polyfill.io/v3/polyfill.min.js?features=es6
      - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
    ```

## Magiclink

Automatically recognizes links in markdown: www.google.com

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - pymdownx.magiclink
    ```

## Tables

https://squidfunk.github.io/mkdocs-material/reference/data-tables/

https://squidfunk.github.io/mkdocs-material/reference/data-tables/

|  Method  |   Description   |
|----------|-----------------|
| `GET`    | Fetch resource  |
| `PUT`    | Update resource |
| `DELETE` | Delete resource |


??? tldr "Config"
    None!

## References

- https://python-markdown.github.io/extensions/
- http://madrus4u.com/mdocs/engine/styling/
- https://code.kx.com/q/about/sg/ 
- https://facelessuser.github.io/pymdown-extensions/
