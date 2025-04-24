.PHONY: install test lint format clean run dev docker-build docker-run

# Variáveis
PYTHON := python
PIP := pip
PYTEST := pytest
MYPY := mypy
BLACK := black
DOCKER := docker
COMPOSE := docker-compose

# Comandos principais
install:
	$(PIP) install -e .

test:
	$(PYTEST)

lint:
	$(MYPY) src
	$(BLACK) --check src tests

format:
	$(BLACK) src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +

run:
	$(PYTHON) examples/dashboard_example.py

dev:
	uvicorn src.web.app:app --host 0.0.0.0 --port 8050 --reload

# Comandos Docker
docker-build:
	$(DOCKER) build -t options-center .

docker-run:
	$(DOCKER) run -p 8050:8050 --env-file .env options-center

# Comandos Docker Compose
up:
	$(COMPOSE) up

up-dev:
	$(COMPOSE) up dev

down:
	$(COMPOSE) down

test-docker:
	$(COMPOSE) --profile test up test