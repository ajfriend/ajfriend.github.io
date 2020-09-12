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

??? example "Code"
    ```md
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


??? example "Code"
    ```md
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

??? example "Code"
    ```md
    For en-dash, (--), em-dash (---), and ellipsis (...).
    ```

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - smarty
    ```

## Math

In-line and block math to find an
$x \in \lbrace y \mid 0 \preceq y \preceq \mathbf{1} \rbrace$:

$$
\begin{array}{ll}
\mbox{minimize}
& (1/2)\|Ax-b\|_2^2 + \lambda \|x\|_1 \\
\mbox{subject to}
& 0 \preceq x \preceq \mathbf{1} \\
& \|x\|_2 \leq 1,
\end{array}
$$

??? example "Code"
    ```md
    In-line and block math to find an
    $x \in \lbrace y \mid 0 \preceq y \preceq \mathbf{1} \rbrace$:

    $$
    \begin{array}{ll}
    \mbox{minimize}
    & (1/2)\|Ax-b\|_2^2 + \lambda \|x\|_1 \\
    \mbox{subject to}
    & 0 \preceq x \preceq \mathbf{1} \\
    & \|x\|_2 \leq 1,
    \end{array}
    $$
    ```

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


??? example "Code"
    ```md
    |  Method  |   Description   |
    |----------|-----------------|
    | `GET`    | Fetch resource  |
    | `PUT`    | Update resource |
    | `DELETE` | Delete resource |
    ```

??? tldr "Config"
    None!

## Definition list

`Lorem ipsum dolor sit amet`
:   Sed sagittis eleifend rutrum. Donec vitae suscipit est. Nullam tempus
    tellus non sem sollicitudin, quis rutrum leo facilisis.

`Cras arcu libero`
:   Aliquam metus eros, pretium sed nulla venenatis, faucibus auctor ex. Proin
    ut eros sed sapien ullamcorper consequat. Nunc ligula ante.

    Duis mollis est eget nibh volutpat, fermentum aliquet dui mollis.
    Nam vulputate tincidunt fringilla.
    Nullam dignissim ultrices urna non auctor.

??? example "Code"
    ```md
    `Lorem ipsum dolor sit amet`
    :   Sed sagittis eleifend rutrum. Donec vitae suscipit est. Nullam tempus
        tellus non sem sollicitudin, quis rutrum leo facilisis.

    `Cras arcu libero`
    :   Aliquam metus eros, pretium sed nulla venenatis, faucibus auctor ex. Proin
        ut eros sed sapien ullamcorper consequat. Nunc ligula ante.

        Duis mollis est eget nibh volutpat, fermentum aliquet dui mollis.
        Nam vulputate tincidunt fringilla.
        Nullam dignissim ultrices urna non auctor.
    ```

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - def_list
    ```

## Task list

* [x] Lorem ipsum dolor sit amet, consectetur adipiscing elit
* [ ] Vestibulum convallis sit amet nisi a tincidunt
    * [x] In hac habitasse platea dictumst
    * [x] In scelerisque nibh non dolor mollis congue sed et metus
    * [ ] Praesent sed risus massa
* [ ] Aenean pretium efficitur erat, donec pharetra, ligula non scelerisque

??? example "Code"
    ```md
    * [x] Lorem ipsum dolor sit amet, consectetur adipiscing elit
    * [ ] Vestibulum convallis sit amet nisi a tincidunt
        * [x] In hac habitasse platea dictumst
        * [x] In scelerisque nibh non dolor mollis congue sed et metus
        * [ ] Praesent sed risus massa
    * [ ] Aenean pretium efficitur erat, donec pharetra, ligula non scelerisque
    ```

??? tldr "Config"
    ```yaml
    markdown_extensions:
      - pymdownx.tasklist:
          custom_checkbox: true
    ```

## References

- https://python-markdown.github.io/extensions/
- http://madrus4u.com/mdocs/engine/styling/
- https://code.kx.com/q/about/sg/ 
- https://facelessuser.github.io/pymdown-extensions/
