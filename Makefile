.PHONY: dev test migrate lint help

dev:
	docker compose up --build

test:
	docker compose run --rm api python -m pytest backend/tests -q

migrate:
	docker compose run --rm api alembic -c backend/alembic.ini upgrade head

lint:
	docker compose run --rm api python -m ruff check backend/app

help:
	@echo "Targets:"
	@echo "  dev      - Start all services (db, api, web, worker)"
	@echo "  test     - Run backend tests"
	@echo "  migrate  - Run database migrations"
	@echo "  lint     - Run ruff linter"