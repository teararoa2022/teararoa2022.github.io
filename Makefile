clean:
	rm -rf _site .jekyll-cache

serve: clean
	open http://127.0.0.1:4000/
	bundle exec jekyll serve --incremental

install:
	pip install -r requirements.txt

dev-install: install
	pre-commit install