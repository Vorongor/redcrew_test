makemigrations:
	docker compose exec api uv run alembic revision --autogenerate -m "$(msg)"

migrate:
	docker compose exec api uv run alembic upgrade head

up in dev mode:
    docker compose up --watch