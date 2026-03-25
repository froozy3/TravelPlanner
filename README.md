# Travel Planner API

REST API for trip projects and places, integrated with the [Art Institute of Chicago API](https://api.artic.edu/docs/).

**Stack:** FastAPI · SQLAlchemy 2 (async) · SQLite (aiosqlite) · Pydantic v2 · httpx · TTL cache for external API responses.

## Assessment scope & bonus items

This project was built for a **Travel Planner** backend test (CRUD REST API, SQLite, Art Institute of Chicago API for place validation, business rules: 1–10 places per project, no duplicate external IDs per project, project deletion blocked if any place is visited, `is_completed` when all places are visited).

**Bonus requirements — what is implemented**

| Bonus | Status |
|--------|--------|
| **Docker** (`Dockerfile` / `docker-compose`) | Implemented — see [Quick start (Docker)](#quick-start-docker--macos--windows). |
| **API documentation** (Postman *or* OpenAPI/Swagger) | **OpenAPI/Swagger** via FastAPI — [http://localhost:8000/docs](http://localhost:8000/docs) and [http://localhost:8000/redoc](http://localhost:8000/redoc). No Postman collection file in the repo. |
| **Pagination / filtering** on list endpoints | **Implemented** — see [List endpoints](#list-endpoints-pagination--filters) below. |
| **Caching** third-party API responses | Implemented — in-memory TTL cache (`cachetools.TTLCache`) in `app/clients/art_institute.py` for artwork validation. |
| **Basic authentication** | Not implemented (out of scope). |
| **Code quality** (structure, commits) | Layered layout (`api` / `services` / `models` / `clients`). Commit history quality is up to how you publish the repo. |

## Local URLs

After the server is running, open:

| What        | URL |
|-------------|-----|
| API root    | [http://localhost:8000](http://localhost:8000) |
| Swagger UI  | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ReDoc       | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| Health      | [http://localhost:8000/health](http://localhost:8000/health) |

API version prefix: **`/api/v1`** — e.g. `/api/v1/projects`, `/api/v1/places`.

*(You can also use `http://127.0.0.1:8000` — same machine, same service.)*

## List endpoints: pagination & filters

| Endpoint | Pagination | Filters |
|----------|------------|---------|
| `GET /api/v1/projects` | `offset` (default `0`), `limit` (default `100`, max `500`) | `name_contains` — case-insensitive substring on name; `is_completed` — `true` / `false`; `start_date_from`, `start_date_to` — inclusive calendar-day range on `start_date` |
| `GET /api/v1/places/project/{project_id}` | — | — (returns all places for the project) |

Try in Swagger: [http://localhost:8000/docs](http://localhost:8000/docs).

### Quick manual checks (curl)

Boolean filters use real booleans in the query string (`true` / `false`), not quoted strings.

```bash
# Projects: first page, 2 items per page
curl -s "http://localhost:8000/api/v1/projects/?offset=0&limit=2"

# Projects: only completed (boolean true)
curl -s "http://localhost:8000/api/v1/projects/?is_completed=true"

# Projects: not completed (boolean false)
curl -s "http://localhost:8000/api/v1/projects/?is_completed=false"

# Places in project 1 (all)
curl -s "http://localhost:8000/api/v1/places/project/1"

# Delete place by id
curl -s -X DELETE "http://localhost:8000/api/v1/places/42"
```

### Automated tests

```bash
pip install -r requirements.txt
pytest tests/test_pagination.py -v
```

## Quick start (Docker) — macOS & Windows

From the project root:

```bash
docker compose up --build
```

Then use the [local URLs](#local-urls) above.

## Local run (no Docker)

**Prerequisites:** Python 3.12+

### macOS / Linux

```bash
cd /path/to/TravelPlanner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Optional: `python app/main.py` (run from the repository root with the venv active).

### Windows (Command Prompt)

```bat
cd C:\path\to\TravelPlanner
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Windows (PowerShell)

```powershell
cd C:\path\to\TravelPlanner
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then use the [local URLs](#local-urls) above.

## Configuration

Create a `.env` file in the project root (see `app/core/config.py`):

| Variable        | Default |
|----------------|---------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./travel_planner.db` |
| `PROJECT_NAME` | `Travel Planner API` |

## Project layout

- `app/main.py` — FastAPI app and route wiring
- `app/api/routes/` — HTTP endpoints
- `app/services/` — business logic
- `app/models/` — ORM models
- `app/clients/` — Art Institute API client

## VS Code debug

Use `.vscode/launch.json` → **Debug FastAPI (uvicorn)**.
