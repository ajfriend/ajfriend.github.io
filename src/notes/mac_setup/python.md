# Python setup

I'm using `pyenv` to manage the overall "system" Python.

```sh
brew install python
brew install pyenv
```

Following the [`pyenv` instructions](https://github.com/pyenv/pyenv), we need
to make sure the following is at the end of the shell configuration:

```sh
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
```

Since we're using Oh My Zsh, we can put it into a file like
`~/.oh-my-zsh/custom/for_pyenv.zsh` using the command

```sh
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.oh-my-zsh/custom/for_pyenv.zsh
```

Make sure to restart the shell to activate the changes.

We then need to install any [Python build dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
before trying to add a new version of Python. Use the following:

```sh
brew install openssl readline sqlite3 xz zlib
```

??? caution "Issues with `zlib`"
    Note that you may see the warning below from `brew`:

    ```
    zlib is keg-only, which means it was not symlinked into /usr/local,
    because macOS already provides this software and installing another version in
    parallel can cause all kinds of trouble.

    For compilers to find zlib you may need to set:
      export LDFLAGS="-L/usr/local/opt/zlib/lib"
      export CPPFLAGS="-I/usr/local/opt/zlib/include"

    For pkg-config to find zlib you may need to set:
      export PKG_CONFIG_PATH="/usr/local/opt/zlib/lib/pkgconfig"
    ```

    In that case, something like the flow below should work
    (based on this [Stack Overflow answer](https://stackoverflow.com/a/54955286/3298754)):

    ```sh
    brew install zlib
    export LDFLAGS="-L/usr/local/opt/zlib/lib"
    export CPPFLAGS="-I/usr/local/opt/zlib/include"
    pyenv install 3.7.2
    ```

### Debugging `pyenv`

This page is pretty good: https://github.com/pyenv/pyenv/wiki/Common-build-problems

I was seeing this issue:

```
> virtualenv
/Users/ajfriend/.pyenv/shims/virtualenv: line 21: /usr/local/Cellar/pyenv/1.2.20/libexec/pyenv: No such file or directory
```

but this was [fixed by running](https://github.com/Homebrew/brew/issues/1457) `pyenv rehash`.

### References

- https://opensource.com/article/19/5/python-3-default-mac
- https://realpython.com/intro-to-pyenv/
- https://github.com/pyenv/pyenv

But then still use `virualenv` to make environments per repo.

```sh
pyenv versions
which python
which pip
```

## playing

WARNING: The Python bz2 extension was not compiled. Missing the bzip2 lib?

ooh, might also want brew install bzip2

export LDFLAGS="-L/usr/local/opt/zlib/lib -L/usr/local/opt/bzip2/lib"
export CPPFLAGS="-I/usr/local/opt/zlib/include -I/usr/local/opt/bzip2/include"
pyenv install 3.9.0

pyenv versions -- lists the currently installed pythons
pyenv install --list -- list all available python verions
pyenv install 2.6.8 --installs a version of python
pyenv versions -- shows currently installed python versions, * next to active
pyenv uninstall <version> 
pyenv version -- shows currently active python
pyenv global 2.7.6 -- set the python

❯ pyenv which pip
/Users/ajfriend/.pyenv/versions/3.8.5/bin/pip

-- Displays the full path to the executable that pyenv will invoke when you run the given command.


## virtual environments

(choose python version with `pyenv`)

`python -m venv env`
