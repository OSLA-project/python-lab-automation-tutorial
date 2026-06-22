
.PHONY: serve build generate-docs

serve: generate-docs
	mkdocs serve --livereload

generate-docs:
	python generate_docs.py

build: generate-docs
	mkdocs build
