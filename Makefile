.PHONY: help install install-dev compile-deps update-deps test lint clean

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install production dependencies
	pip install -r requirements.txt

install-dev:  ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	pip install -e .

compile-deps:  ## Compile .in files to .txt with exact versions (requires pip-tools)
	pip install pip-tools
	pip-compile --resolver=backtracking --output-file=requirements.txt requirements.in
	pip-compile --resolver=backtracking --output-file=requirements-dev.txt requirements-dev.in

update-deps:  ## Update all dependencies to latest compatible versions
	pip install pip-tools
	pip-compile --upgrade --resolver=backtracking --output-file=requirements.txt requirements.in
	pip-compile --upgrade --resolver=backtracking --output-file=requirements-dev.txt requirements-dev.in

freeze:  ## Generate requirements.txt from current environment (alternative to pip-tools)
	pip freeze > requirements-frozen.txt
	@echo "Generated requirements-frozen.txt with exact versions"

test:  ## Run tests with coverage
	pytest --cov=src/sbom_merger --cov-report=term-missing --cov-report=html --cov-fail-under=96 -v

lint:  ## Run all linters
	black --check src/ tests/
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/sbom_merger --ignore-missing-imports

format:  ## Format code with black
	black src/ tests/

security:  ## Run security checks
	bandit -r src/
	safety check

clean:  ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
