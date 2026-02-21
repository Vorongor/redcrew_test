Here is a professional and clean **README.md** for your project. It covers the
modern stack you've chosen (`uv`, `FastAPI`, `Docker Compose Watch`) and
clearly explains the business logic and external integration.

---

# 🌍 Travel Planner API

A modern FastAPI service for managing travel projects and art-inspired
destinations, integrated with the **Art Institute of Chicago API**.

## 🚀 Features

* **Project Management**: Create, update, and track travel projects.
* **Art Institute Integration**: Add places to your trips using real artwork
  IDs from the [Art Institute of Chicago](https://api.artic.edu/docs/).
* **Business Validation**:
* **Visited Guard**: Projects cannot be deleted if any associated places are
  marked as "visited."
* **Place Limits**: Maximum of 10 places per project to keep your itinerary
  focused.
* **Uniqueness**: Prevent adding the same artwork to the same project multiple
  times.
* **External Verification**: All places are validated against the Art Institute
  API before being saved.

## 🛠 Tech Stack

* **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
* **Dependency Manager**: [uv](https://github.com/astral-sh/uv) (Extremely fast
  Python package installer)
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
   Create a `.env` file based on your configuration (you may use .env.sample):

```env
POSTGRES_DB=travel_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql+asyncpg://postgres:postgres@project_db:5432/travel_db

```

3. **Run with Hot Reload (Docker Compose Watch)**:
   This mode automatically syncs your code changes and rebuilds the image if
   `pyproject.toml` changes.

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

* **Swagger UI
  **: [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs)

---

### 🔑 API Endpoints Reference

#### 🛡️ Authentication

| Method | Endpoint           | Description                                                       |
|--------|--------------------|-------------------------------------------------------------------|
| `POST` | `/api/v1/users`    | **Register**: Create a new user account                           |
| `POST` | `/api/v1/sessions` | **Login**: Authenticate and receive Access & Refresh tokens       |
| `POST` | `/api/v1/refresh`  | **Refresh**: Issue a new access token using a valid refresh token |
| `POST` | `/api/v1/logout`   | **Logout**: Invalidate the current session                        |

#### 🗺️ Travel Projects

| Method   | Endpoint                | Description                                        |
|----------|-------------------------|----------------------------------------------------|
| `GET`    | `/api/v1/projects/`     | List all travel projects (paginated)               |
| `POST`   | `/api/v1/projects/`     | Create a project (can include an array of places)  |
| `GET`    | `/api/v1/projects/{id}` | Get detailed information about a single project    |
| `PATCH`  | `/api/v1/projects/{id}` | Update project metadata (Name, Description, Date)  |
| `DELETE` | `/api/v1/projects/{id}` | Remove project (Blocked if any place is "visited") |

#### 📍 Places & Destinations

| Method  | Endpoint                       | Description                                                 |
|---------|--------------------------------|-------------------------------------------------------------|
| `GET`   | `/api/v1/projects/{id}/places` | List all places assigned to a specific project              |
| `POST`  | `/api/v1/projects/{id}/places` | Add a place (validates `external_id` via Art Institute API) |
| `GET`   | `/api/v1/places/{id}`          | Get detailed information about a specific place             |
| `PATCH` | `/api/v1/places/{id}`          | Update specific place (Notes, Visited status)               |

---

### 💡 Pro-Tips for using the API:

* **Nested Creation**: You can create a project and its places in one
  `POST /projects/` call, provided you don't exceed the **10-place limit**.
* **Security**: All endpoints (except Register and Login) require a
  `Bearer <access_token>` in the Authorization header.
* **Validation**: If you try to delete a project with visited places, the API
  will return a `400 Bad Request` with a descriptive error.

---
![img.png](img.png)

## 📂 Project Structure

```text
├── src/
│   ├── auth/           # Router for user authentication
│   │   └── security/   # Contains security logic
│   ├── config/         # Contains project configuration
│   ├── database/       # DB session and Base model
│   │   └── models/     # SQLAlchemy ORM models
│   ├── migrations/     # Alembic migration versions
│   ├── travel/         # External API logic (Art Institute)
│   │   ├── place/      # Contains Place crud, schemas, router and service
│   │   └── project/    # Contains Project crud, schemas and router
│   ├── api.py          # API entry point include all routers and set version
│   └── main.py         # App entrypoint
├── alembic.ini         # Alembic config
├── pyproject.toml      # uv dependencies
├── Dockerfile          # Main Image for app 
└── compose.yml         # Local development setup

```