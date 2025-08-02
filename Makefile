.PHONY: help install install-dev test test-unit test-integration coverage lint format type-check clean run init-db seed-db

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run linting (flake8)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make type-check    - Run type checking with mypy"
	@echo "  make clean         - Remove cache files"
	@echo "  make run           - Run the development server"
	@echo "  make init-db       - Initialize the database"
	@echo "  make seed-db       - Seed the database with sample data"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

coverage:
	pytest --cov=app --cov-report=html --cov-report=term-missing

lint:
	flake8 app tests

format:
	black app tests scripts
	isort app tests scripts

type-check:
	mypy app

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	python run.py

init-db:
	python scripts/init_db.py

seed-db:
	python scripts/seed_data.py

# Development workflow commands
dev-setup: install-dev init-db seed-db
	@echo "Development environment ready!"

check: lint type-check test
	@echo "All checks passed!"

# Docker commands (for future use)
docker-build:
	docker build -t prompt-manager .

docker-run:
	docker run -p 5001:5001 prompt-manager