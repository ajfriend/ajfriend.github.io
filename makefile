.PHONY: env serve purge

env:
	virtualenv -p python3 env
	env/bin/pip install --upgrade pip
	env/bin/pip install -r requirements.txt

purge:
	-@rm -rf env

build:
	env/bin/mkdocs build

serve:
	open http://127.0.0.1:8000
	env/bin/mkdocs serve
