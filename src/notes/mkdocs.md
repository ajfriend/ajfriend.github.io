# Setting up a personal site with MkDocs

I'm serving this site via a [Github Pages](https://pages.github.com/).

There are two ways to do this:

1. As a **"user or organization site"**, which means it is published from
the `master` branch of of a repo named like `<username>.github.io`, and is
published at `http://username.github.io/`.

2. As a **"project site"**, which is served from a specific branch (like `gh-pages`)
of an existing project's repo, and is---published at
`http://username.github.io/repository`.

This site uses the first approach,
to get the fancy-schmancy http://ajfriend.github.io/ URL.

```python
import tensorflow as tf

def foo():
    print('hello')
```


## Config

https://python-markdown.github.io/extensions/ for em-dash and ellipsis...

enabled with

```yml
markdown_extensions:
  - smarty
```

## Helpful sites

- https://python-markdown.github.io/extensions/
- http://madrus4u.com/mdocs/engine/styling/
- https://code.kx.com/q/about/sg/ 
- https://facelessuser.github.io/pymdown-extensions/
