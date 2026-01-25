.PHONY: help install test smoke regression lint format report clean

help:
	@echo "Available commands:"
	@echo "  make install     Install dependencies"
	@echo "  make test        Run all tests"
	@echo "  make smoke       Run smoke tests only"
	@echo "  make regression  Run regression tests"
	@echo "  make lint        Run linter (ruff)"
	@echo "  make format      Auto-format code"
	@echo "  make report      Run tests with HTML + JUnit report"
	@echo "  make clean       Remove caches and artifacts"

install:
	pip install -U pip
	pip install -e .

test:
	pytest

smoke:
	pytest -m smoke

regression:
	pytest -m regression

lint:
	ruff check .

format:
	ruff format .

report:
	mkdir -p artifacts
	pytest --junitxml=artifacts/junit.xml --html=artifacts/report.html

clean:
	rm -rf .pytest_cache __pycache__ artifacts .coverage htmlcov
