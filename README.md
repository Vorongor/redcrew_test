Here is a professional and clean **README.md** for your project. It covers the modern stack you've chosen (`uv`, `FastAPI`, `Docker Compose Watch`) and clearly explains the business logic and external integration.

---

# 🌍 Travel Planner API

A modern FastAPI service for managing travel projects and art-inspired destinations, integrated with the **Art Institute of Chicago API**.

## 🚀 Features

* **Project Management**: Create, update, and track travel projects.
* **Art Institute Integration**: Add places to your trips using real artwork IDs from the [Art Institute of Chicago](https://api.artic.edu/docs/).
* **Business Validation**:
* **Visited Guard**: Projects cannot be deleted if any associated places are marked as "visited."
* **Place Limits**: Maximum of 10 places per project to keep your itinerary focused.
* **Uniqueness**: Prevent adding the same artwork to the same project multiple times.
* **External Verification**: All places are validated against the Art Institute API before being saved.



## 🛠 Tech Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **Dependency Manager**: [uv](https://github.com/astral-sh/uv) (Extremely fast Python package installer)
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy 2.0 (Async)
* **Migrations**: Alembic
* **Containerization**: Docker with **Compose Watch** support

---

## 🚦 Getting Started

### Prerequisites

* Docker and Docker Compose (v2.22.0+ for Watch support)

### Installation & Development

1. **Clone the repository**:
```bash
  git clone <your-repo-url>
  cd travel-planner

```


2. **Set up Environment Variables**:
Create a `.env` file based on your configuration:
```env
POSTGRES_DB=travel_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+asyncpg://postgres:postgres@project_db:5432/travel_db

```


3. **Run with Hot Reload (Docker Compose Watch)**:
This mode automatically syncs your code changes and rebuilds the image if `pyproject.toml` changes.
```bash
docker compose up --watch

```


4. **Run Migrations**:
In a new terminal:
```bash
docker compose exec api uv run alembic upgrade head

```



---

## 📖 API Documentation

Once the server is running, explore the interactive documentation:

* **Swagger UI**: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)
* **ReDoc**: [http://localhost:8000/redoc](https://www.google.com/search?q=http://localhost:8000/redoc)

### Key Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/projects/` | Create a project (optionally with places) |
| `GET` | `/projects/` | List all projects |
| `DELETE` | `/projects/{id}` | Remove project (fails if places visited) |
| `POST` | `/projects/{id}/places` | Add a validated Art Institute place |
| `PATCH` | `/places/{id}` | Update notes or mark as visited |

---

## 📂 Project Structure

```text
├── src/
│   ├── api/            # Router definitions
│   ├── database/       # DB session and Base model
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic validation schemas
│   ├── services/       # External API logic (Art Institute)
│   ├── crud/           # Database operations
│   └── main.py         # App entry point
├── migrations/         # Alembic migration versions
├── pyproject.toml      # uv dependencies
└── docker-compose.yml  # Local development setup

```

---

## 🧪 Running Tests

*(Optional: Add your testing instructions here)*

```bash
docker compose exec api uv run pytest

```

---

**Would you like me to add a "Troubleshooting" section or specific instructions on how to use the `uv` commands inside Docker?**