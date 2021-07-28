.PHONY: init purge build serve

# use pyenv to set the python version before running this
init: purge
	python -m venv env
	env/bin/pip install --upgrade pip setuptools wheel
	env/bin/pip install -r requirements.txt

purge:
	-@rm -rf env site
	-@rm -rf .DS_Store .pytest_cache

build:
	env/bin/mkdocs build

serve:
	open http://127.0.0.1:8000
	env/bin/mkdocs serve
