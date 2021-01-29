# Python setup

I'm using `pyenv` to manage the overall "system" Python, and `venv` to manage
per-project virtual environments.

`pyenv` allows you to install multiple versions of Python on your system
and switch between them. You can manage a global Python, or have more
specific rules like per-directory or per shell. We'll just use
it for our system Python since `venv` will handle the virtual environments
for each project.
One nice thing about `pyenv` is that it is **independent** of any Python
install on your system, since it is just a collection of shell scripts.

## Set up `pyenv`

```sh
brew install pyenv
```

Following the [`pyenv` instructions](https://github.com/pyenv/pyenv), we need
to make sure the following is at the end of the shell configuration:

```sh
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
```

Since [we're using Oh My Zsh](../shell), we can put it into a file like
`~/.oh-my-zsh/custom/for_pyenv.zsh` using the command

```sh
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.oh-my-zsh/custom/for_pyenv.zsh
```

Make sure to restart the shell to activate the changes.

## Preparing for installing new Pythons

We then need to install any [Python build dependencies](https://github.com/pyenv/pyenv/wiki#suggested-build-environment)
before trying to add a new version of Python. Use the following:

```sh
brew install openssl readline sqlite3 xz zlib
```

New versions of Python can then be installed with a command like

```sh
pyenv install 2.7.8
```

### Debugging

This page is pretty good: https://github.com/pyenv/pyenv/wiki/Common-build-problems

I was seeing this issue:

```
> virtualenv
/Users/ajfriend/.pyenv/shims/virtualenv: line 21: /usr/local/Cellar/pyenv/1.2.20/libexec/pyenv: No such file or directory
```

but this was [fixed by running](https://github.com/Homebrew/brew/issues/1457) `pyenv rehash`.

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


??? caution "WARNING: The Python bz2 extension was not compiled. Missing the bzip2 lib?"
    In this case, `brew install bzip2`. You may also need to set compiler
    flags. If you need to set flags for both `zlib` and `bz2`, you can
    concatenate the flags like

    ```sh
    export LDFLAGS="-L/usr/local/opt/zlib/lib -L/usr/local/opt/bzip2/lib"
    export CPPFLAGS="-I/usr/local/opt/zlib/include -I/usr/local/opt/bzip2/include"
    pyenv install 3.9.0
    ```

??? caution "`numpy` issues with Python 3.9"

    I was seeing an error like `RuntimeError: Polyfit sanity test emitted a warning...`

    This was fixed with (and potentially in addition to the fixes above):

    ```sh
    export OPENBLAS="$(brew --prefix openblas)"
    pyenv install 3.9.0
    ```

    A `pip cache remove numpy` may or may not have helped, too.


## `pyenv` commands

- `pyenv versions`

    shows all installed Python versions; `*` denotes the one currently active

    ```sh
    ❯ pyenv versions
    * system (set by /Users/ajfriend/.pyenv/version)
      3.7.9
      3.8.5
      3.9.0
    ```

- `pyenv install --list`

    list all Python versions available for installation

- `pyenv install 2.6.8`

    installs a version of python

- `pyenv uninstall <version>`
- `pyenv version`
    
    shows currently active Python

    ```sh
    ❯ pyenv version
    3.9.0 (set by /Users/ajfriend/.pyenv/version)
    ```

- `pyenv global 2.7.6`

    set the "global/system" Python

- `pyenv which <command>`
    
    Displays the full path to the executable that `pyenv` will invoke when you
    run the given command

    ```sh
    ❯ pyenv which pip
    /Users/ajfriend/.pyenv/versions/3.9.0/bin/pip
    ```

## Using `venv` for virtual environments

`pyenv` can help you manage virtual environments, but I prefer to do things
manually with `venv`.

I'll generally make a virtual environment for each separate project within
that project's folder. To do this, first select the version of Python
you'd like to use for the virtual environment:

```sh
pyenv versions
pyenv global 3.7.9
```

Then, within the project directory, run

```sh
python -m venv env
```

which will create a virtual environment in the `env` directory.

Now you can activate/deactivate your environment, or just run things directly
with commands like:

```sh
env/bin/python
env/bin/pip
env/bin/jupyter lab
```


## Disabling `pyenv`

`pyenv global system` will set things back to the "system" Python,
but `pyenv` is still handling the logic that determines which Python to use.

To stop `pyenv` from using its shims to determine which Python to use,
just remove the `pyenv init` code that we added above to our shell config file.

For more details, see https://github.com/pyenv/pyenv#uninstalling-pyenv.

## `pyenv` references

- [Stop Homebrew Version-Jacking Your Python All The Time](https://matt.sh/unify-python)
- https://opensource.com/article/19/5/python-3-default-mac
- https://realpython.com/intro-to-pyenv/
- https://github.com/pyenv/pyenv
