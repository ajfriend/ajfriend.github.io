# MkDocs on Github Pages

I'm serving this site via a [Github Pages](https://pages.github.com/).

There are two ways to do this:

1. As a **"user or organization site"**, which means it is published from
the `master` branch (necessarily?) of of a repo named like `<username>.github.io`, and is
published at `http://username.github.io/`.

2. As a **"project site"**, which is served from a specific branch (like `gh-pages`)
of an existing project's repo, and is---published at
`http://username.github.io/repository`.

This site uses the first approach,
to get the fancy-schmancy http://ajfriend.github.io/ URL.

## Publishing from `master`

We [configure the repo](https://github.com/ajfriend/ajfriend.github.io/settings)
to serve the website from the `docs` folder on the
`master` branch. This means we need to commit all the built website files to
git, which is not ideal because:

1. the process is a manual, and
2. we're adding output files to version control.

![Screenshot](img/github_settings.png)

We also need to configure the `mkdocs.yml` file with
```yaml
docs_dir: src
site_dir: docs
```
so that it knows our markdown source is in `src`, and that it should build
the output website to `docs`.

### Workflow

1. Make changes to the markdown files.
2. View changes locally with `mkdocs serve`.
3. Build the website to `docs` with `mkdocs build`.
4. Commit the changes, especially the entire output folder `docs`, and push
to the upstream `origin` remote on Github.

Github will serve whatever website files are in the `docs` folder after uploading
to Github.

## Publishing from `gh-pages`

**TODO**

Is there an alternative approach that avoid having to build manually and commit
the website files to git?

For example, could I keep only the `src` files on the `master` branch of the
repo, and build the website `docs` to the `gh-pages` branch? I might be able to
setup a hook or GithubAction to do that when I push to the master branch.

That might be what the links below are trying to suggest..

A few different ways using the `gh-pages` approach:

- https://squidfunk.github.io/mkdocs-material/publishing-your-site/
- https://github.com/marketplace/actions/github-pages-action
- https://bluegenes.github.io/mkdocs-github-actions/
