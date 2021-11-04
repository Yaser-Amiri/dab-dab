MAX_LINE_LENGHT := $$(cat "`git rev-parse --show-toplevel`/setup.cfg" | grep "max-line-length" | grep -Eo '[[:digit:]]+')

.PHONY: install-dep
install-dep:
	pip install -r dev-requirements.txt

.PHONY: dev-ready-env
dev-ready-env: install-dep
	cp ./dev/pre-commit.sh .git/hooks/pre-commit
	chmod u+x .git/hooks/pre-commit
	@echo "Done!"

.PHONY: lint
lint:
	black -l $(MAX_LINE_LENGHT) .
	flake8 .

.PHONY: build
build:
	python setup.py sdist bdist_wheel
