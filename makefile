.PHONY: build init purge serve

build:
	env/bin/mkdocs build

init:
	virtualenv -p python3 env
	env/bin/pip install --upgrade pip
	env/bin/pip install -r requirements.txt

purge:
	-@rm -rf env docs
	-@rm -rf .DS_Store

serve:
	open http://127.0.0.1:8000
	env/bin/mkdocs serve

lab:
	env/bin/jupyter lab
