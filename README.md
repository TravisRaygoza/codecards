# CodeCards

A spaced repetition flashcard API for studying programming concepts, built with FastAPI and the SM-2 algorithm. Supports AI-powered card generation via Claude.

## Tech Stack

- **FastAPI** — async Python web framework
- **PostgreSQL** — relational database (async via asyncpg)
- **Redis** — caching layer (cache-aside pattern, 5-min TTL)
- **SQLModel** — ORM (SQLAlchemy + Pydantic)
- **Alembic** — database migrations
- **JWT + bcrypt** — authentication
- **SM-2 Algorithm** — spaced repetition scheduling
- **Claude API** — AI flashcard generation
- **Celery** — async task queue (Redis backend)
- **pytest** — async integration + unit tests

## Features

- **User auth** — signup, login, JWT-protected routes
- **Deck CRUD** — create, read, update, delete flashcard decks with language/topic tags
- **Card CRUD** — Q&A and code-type cards with difficulty ratings and code templates
- **Spaced repetition** — SM-2 algorithm tracks ease factor, interval, and next review date per card
- **Study sessions** — start sessions, submit answers with quality ratings (0–5), track progress
- **AI generation** — generate flashcards from a topic/language/difficulty using Claude, with option to save directly to a deck
- **Redis caching** — cache-aside on deck reads with automatic invalidation on writes
- **Test suite** — async integration tests with isolated test database + SM-2 unit tests

## Project Structure

```
app/
├── main.py                  # FastAPI entry point
├── config.py                # Pydantic settings (env vars)
├── core/
│   └── security.py          # JWT, password hashing, OAuth2
├── database/
│   ├── models.py            # SQLModel database models
│   ├── session.py           # Async engine and session setup
│   └── redis.py             # Redis caching utilities
├── api/
│   ├── router.py            # Router aggregation
│   ├── dependencies.py      # get_current_user dependency
│   ├── routers/
│   │   ├── user.py          # Auth endpoints
│   │   ├── deck.py          # Deck CRUD endpoints
│   │   ├── card.py          # Card CRUD endpoints
│   │   ├── study.py         # Study session endpoints
│   │   └── ai.py            # AI generation endpoints
│   └── schemas/
│       ├── user.py          # User request/response schemas
│       ├── deck.py          # Deck schemas
│       ├── card.py          # Card schemas
│       ├── pagination.py   # Generic paginated response
│       ├── study.py         # Study schemas
│       └── ai.py            # AI schemas
├── services/
│   ├── user.py              # Auth business logic
│   ├── deck.py              # Deck logic + caching
│   ├── card.py              # Card logic
│   ├── study.py             # Session + SM-2 logic
│   ├── ai.py                # Claude API integration
│   └── sm2.py               # SM-2 algorithm implementation
├── worker/
│   └── tasks.py             # Celery task definitions
└── tests/
    ├── conftest.py           # Fixtures (test DB, auth client)
    ├── test_user.py          # Auth endpoint tests
    ├── test_deck.py          # Deck endpoint tests
    ├── test_card.py          # Card endpoint tests
    ├── test_study.py         # Study session tests
    └── test_sm2.py           # SM-2 unit tests
```

## Getting Started

### 1. Start infrastructure

```bash
docker compose up -d
```

This starts PostgreSQL (port 5434) and Redis (port 6381).

### 2. Set up environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5434
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=codecards

REDIS_HOST=localhost
REDIS_PORT=6381

JWT_SECRET_KEY=your_secret_key

ANTHROPIC_API_KEY=your_api_key
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Start the server

```bash
fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`. Interactive docs at `/scalar`.

## Environment Variables

| Variable | Description | Required |
|---|---|---|
| `POSTGRES_SERVER` | PostgreSQL hostname | Yes |
| `POSTGRES_PORT` | PostgreSQL port | Yes |
| `POSTGRES_USER` | PostgreSQL username | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL password | Yes |
| `POSTGRES_DB` | Database name | Yes |
| `REDIS_HOST` | Redis hostname | Yes |
| `REDIS_PORT` | Redis port | Yes |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens | Yes |
| `JWT_ALGORITHM` | JWT algorithm (default: `HS256`) | No |
| `ANTHROPIC_API_KEY` | Claude API key for AI generation | Yes |

## API Endpoints

### Auth

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/user/signup` | Create account |
| `POST` | `/user/login` | Login, returns JWT |
| `GET` | `/user/me` | Get current user profile |

### Decks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/decks/` | Create deck |
| `GET` | `/decks/?page=1&per_page=20` | List user's decks (paginated) |
| `GET` | `/decks/{deck_id}` | Get deck |
| `PATCH` | `/decks/{deck_id}` | Update deck |
| `DELETE` | `/decks/{deck_id}` | Delete deck |

### Cards

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/cards/` | Create card |
| `GET` | `/cards/?deck_id={id}&page=1&per_page=20` | List cards in deck (paginated) |
| `GET` | `/cards/{card_id}` | Get card |
| `PATCH` | `/cards/{card_id}` | Update card |
| `DELETE` | `/cards/{card_id}` | Delete card |

### Study

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/study/sessions` | Start study session |
| `POST` | `/study/sessions/{id}/answer` | Submit answer (quality 0–5) |
| `POST` | `/study/sessions/{id}/end` | End session |
| `GET` | `/study/progress/{deck_id}` | Get SM-2 progress per card |

### AI Generation

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ai/generate` | Generate cards (returns without saving) |
| `POST` | `/ai/generate-and-save/{deck_id}` | Generate and save to deck |

## Running Tests

```bash
# Local
pytest app/tests/ -v

# Via Docker (auto-creates test database)
docker compose run app pytest app/tests/ -v

# SM-2 unit tests only
pytest app/tests/test_sm2.py
```

Tests use a separate `_test` database. The test database is auto-created by `conftest.py` if it doesn't exist. Redis is mocked to avoid event loop conflicts.

CI runs automatically on push/PR to `main` via GitHub Actions.

## Architecture

The app follows a **schema → service → router** pattern:

- **Schemas** (Pydantic models) validate request/response data
- **Services** contain business logic and database operations
- **Routers** define endpoints, handle HTTP concerns, and call services

Authentication is injected via FastAPI's dependency system — protected routes receive the current user through `get_current_user`. Redis caching sits in the service layer with automatic invalidation on mutations.
