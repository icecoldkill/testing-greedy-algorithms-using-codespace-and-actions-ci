.PHONY: help install lint format test clean

help:
	@echo "Available targets:"
	@echo "  install    - Install project dependencies"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code"
	@echo "  test       - Run tests"
	@echo "  clean      - Clean build artifacts"
	@echo "  all        - Run install, lint, format, and test"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pylint black pytest

lint:
	pylint **/*.py --disable=all --enable=E,F

format:
	black . --line-length=88

test:
	pytest -v --cov=. --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

all: install lint format test
	@echo "All steps completed successfully!"