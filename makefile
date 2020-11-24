.PHONY: init build purge serve lab

init: purge
	virtualenv -p python3 env
	env/bin/pip install --upgrade pip
	env/bin/pip install -r requirements-docs.txt

build:
	env/bin/mkdocs build

purge:
	-@rm -rf env docs
	-@rm -rf .DS_Store

serve:
	open http://127.0.0.1:8000
	env/bin/mkdocs serve

lab:
	env/bin/pip install -r requirements-play.txt
	env/bin/jupyter lab
