makemigrations:
	docker compose exec backend uv run alembic revision --autogenerate -m "$(msg)"

migrate:
	docker compose exec backend uv run alembic upgrade head

up in dev mode:
    docker compose up --watch