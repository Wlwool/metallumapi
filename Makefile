PACKAGE := metallum
TEST_DIR := tests
RUN := uv run --frozen --extra dev

.PHONY: setup
setup:
	uv sync --frozen --extra dev

.PHONY: update
update:
	uv lock --upgrade
	$(MAKE) setup

.PHONY: build
build:
	uv build

.PHONY: clean
clean:
	rm -rf dist

.PHONY: format
format:
	$(RUN) ruff check --fix $(PACKAGE) $(TEST_DIR)
	$(RUN) ruff format $(PACKAGE) $(TEST_DIR)

.PHONY: lint
lint:
	$(RUN) ruff check $(PACKAGE) $(TEST_DIR)
	$(RUN) ruff format --check $(PACKAGE) $(TEST_DIR)

.PHONY: typecheck
typecheck:
	$(RUN) mypy $(PACKAGE)

.PHONY: test
test:
	$(RUN) pytest $(TEST_DIR)

.PHONY: checkall
checkall: lint typecheck test build
