# Python setup for Mac

I'm using `pyenv` to manage the overall "system" Python.

- https://opensource.com/article/19/5/python-3-default-mac
- https://realpython.com/intro-to-pyenv/
- https://github.com/pyenv/pyenv

But then still use `virualenv` to make environments per repo.

```sh
pyenv versions
which python
which pip
```

I was seeing this issue:

```
> virtualenv
/Users/ajfriend/.pyenv/shims/virtualenv: line 21: /usr/local/Cellar/pyenv/1.2.20/libexec/pyenv: No such file or directory
```

but this was [fixed by running](https://github.com/Homebrew/brew/issues/1457) `pyenv rehash`.
