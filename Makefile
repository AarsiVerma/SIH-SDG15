.PHONY: dev test migrate lint help retention seed demo-stop

dev:
	docker compose up --build

test:
	docker compose run --rm api python -m pytest backend/tests -q

test-unit:
	docker compose run --rm api python -m pytest backend/tests/unit -q

test-integration:
	docker compose run --rm api python -m pytest backend/tests/integration -q

test-e2e:
	docker compose run --rm api python -m pytest backend/tests/e2e_scenarios -q

migrate:
	docker compose run --rm api alembic -c backend/alembic.ini upgrade head

migrate-create:
	docker compose run --rm api alembic -c backend/alembic.ini revision --autogenerate -m "$(msg)"

lint:
	docker compose run --rm api python -m ruff check backend/app

retention:
	docker compose run --rm retention

retention-dry-run:
	docker compose run --rm retention --dry-run

seed:
	docker compose run --rm api python scripts/seed_demo.py

demo-stop:
	docker compose stop worker

download-models:
	docker compose run --rm api python scripts/download_models.py

help:
	@echo "Targets:"
	@echo "  dev              - Start all services (db, api, web, worker)"
	@echo "  test             - Run all backend tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-e2e         - Run end-to-end tests only"
	@echo "  migrate          - Run database migrations"
	@echo "  migrate-create   - Create new migration (usage: make migrate-create msg='description')"
	@echo "  lint             - Run ruff linter"
	@echo "  retention        - Run data retention cleanup"
	@echo "  retention-dry-run - Show what would be deleted"
	@echo "  seed             - Seed demo data"
	@echo "  demo-stop        - Stop worker for camera failure demo"
	@echo "  download-models  - Download model weights"