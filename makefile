.PHONY: init build purge serve lab

# use pyenv to set the python version before running this
init: purge
	python -m venv env
	env/bin/pip install --upgrade pip setuptools wheel
	env/bin/pip install -r requirements-docs.txt

build:
	env/bin/mkdocs build

purge:
	-@rm -rf env
	-@rm -rf .DS_Store .pytest_cache

serve:
	open http://127.0.0.1:8000
	env/bin/mkdocs serve

lab:
	env/bin/pip install -r requirements-play.txt
	env/bin/jupyter lab
