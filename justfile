build:
	hugo

view:
	hugo server --openBrowser

clean:
	rm -rf public/
	rm -rf resources/
	rm -f .hugo_build.lock
