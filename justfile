_:
	just --list

build:
	hugo

view:
	hugo server --openBrowser

clean:
	just _rm public
	just _rm resources
	just _rm .hugo_build.lock


_rm pattern:
    -@find . -name "{{pattern}}" -prune -exec rm -rf {} +
