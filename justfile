_:
	just --list

build:
	hugo

view:
	# hugo server --openBrowser
	open "http://localhost:1313/blog/cells_to_poly/" & hugo server --port 1313

clean:
	just _rm public
	just _rm resources
	just _rm .hugo_build.lock


_rm pattern:
    -@find . -name "{{pattern}}" -prune -exec rm -rf {} +
