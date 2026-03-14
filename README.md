# SchemaMind Backend

**AI-Powered Natural Language to SQL Engine**

`Version 1.0.0` · `Python / FastAPI` · `PostgreSQL` · `Gemini & Ollama (qwen2.5)`

---

## Overview

SchemaMind Backend is a FastAPI-powered REST API that lets users query any relational database using plain English. Users connect their database, ask questions in natural language, and the system automatically generates and executes the appropriate SQL — returning both the raw results and a human-readable explanation.

The system supports two LLM backends out of the box: **Google Gemini** (cloud/online) and **Ollama** (local/offline). A factory pattern makes switching between them seamless. Role-based access control (RBAC) ensures that the SQL operations an LLM may generate are strictly limited by the authenticated user's permission level — viewers may only SELECT, analysts may INSERT, and admins have full access.

Schema extraction runs automatically when a new database connection is registered. The full schema snapshot (tables, columns, primary keys, foreign keys) is cached in the application's own PostgreSQL instance and injected into every LLM prompt, giving the model the context it needs to produce accurate queries without any manual configuration.

> **Schema Context Optimization (Vector DB / RAG) is not yet implemented.** In the current version (v1), the full schema snapshot is passed as plain text in every prompt. For databases with large schemas this may reduce prompt efficiency. A smarter, embedding-based schema retrieval layer using a Vector DB is planned for **Version 2**.

---

## Key Features

- Natural Language to SQL — ask questions in plain English, get accurate SQL and human-readable answers
- Dual LLM Support — Google Gemini (online) or Ollama / qwen2.5 (local, fully offline)
- Multi-Database Support — PostgreSQL, MySQL, SQLite (Oracle & SQL Server stubs ready)
- Role-Based Access Control — SELECT_ONLY / READ_WRITE / ADMIN_ACCESS permission tiers
- Automatic Schema Extraction & Caching — schema captured on connection, refreshable on demand
- Encrypted DB Credentials — Fernet symmetric encryption via the `cryptography` library
- Persistent Chat History — multi-turn conversations with full message context passed to the LLM
- Auto Chat Titles — LLM generates a session title from the first user message
- SQL Safety Guard — validates the generated SQL operation type against the user's permission before execution
- Alembic Migrations — fully versioned database schema management

---

## Technology Stack

| Layer | Technology |
|---|---|
| API Framework | FastAPI 0.135.1 + Uvicorn |
| ORM & Migrations | SQLAlchemy 2.0.48 + Alembic 1.18.4 |
| Application DB | PostgreSQL (psycopg2) |
| Target DB Drivers | psycopg2 (PostgreSQL), PyMySQL (MySQL), SQLite built-in |
| LLM — Online | Google Gemini (`google-genai` 1.66.0) |
| LLM — Local | Ollama HTTP API (default model: `qwen2.5:3b`) |
| Authentication | JWT (`python-jose`) + bcrypt password hashing |
| Credential Encryption | Fernet symmetric encryption (`cryptography` 46.0.5) |
| Validation | Pydantic v2 + pydantic-settings |
| SQL Parsing | sqlparse 0.5.5 |
| Python Version | 3.13+ |

---

## Project Structure

```
schema-mind-backend/
├── main.py                              # FastAPI application entry point
├── alembic.ini                          # Alembic migration configuration
├── requirements.txt                     # Python dependencies (pinned versions)
├── generate_key.py                      # Utility: generate Fernet encryption key
├── .env.example                         # Environment variable template
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── dependencies.py          # JWT auth dependency injection
│   │       └── routes/
│   │           ├── auth.py              # Register / Login endpoints
│   │           ├── db_connection.py     # DB connection CRUD + schema operations
│   │           └── chat.py              # Chat session & message endpoints
│   │
│   ├── core/
│   │   ├── config.py                    # Pydantic settings (reads .env)
│   │   ├── encryption.py               # Fernet encrypt/decrypt helpers
│   │   ├── hashing.py                  # bcrypt password hashing
│   │   ├── jwt.py                      # JWT creation & verification
│   │   ├── query_guard.py              # Validates SQL op type vs user permission
│   │   ├── sql_permissions.py          # Permission → allowed SQL operations map
│   │   ├── error_handler.py            # Error response formatters
│   │   └── exception_handler.py        # FastAPI global exception handlers
│   │
│   ├── db/
│   │   ├── base.py                     # SQLAlchemy declarative base
│   │   ├── session.py                  # Application DB session factory
│   │   └── engine_creator.py           # Dynamic engine factory for target DBs
│   │
│   ├── llm/
│   │   ├── base_llm.py                 # Abstract LLM interface (ABC)
│   │   ├── gemini_client.py            # Google Gemini implementation
│   │   ├── ollama_client.py            # Ollama (local) implementation
│   │   ├── llm_factory.py              # Factory: returns correct LLM by mode
│   │   └── prompt_builder.py           # Prompt templates (SQL, answer, title)
│   │
│   ├── models/
│   │   ├── user.py                     # User SQLAlchemy model
│   │   ├── db_connection.py            # DbConnection + SchemaCache models
│   │   ├── chat.py                     # ChatSession + ChatMessage models
│   │   └── log.py                      # AuditLog model
│   │
│   ├── repositories/
│   │   ├── auth_repository.py          # User DB queries
│   │   ├── db_connection_repository.py # Connection & schema cache queries
│   │   └── chat_repository.py          # Session & message queries
│   │
│   ├── schemas/
│   │   ├── base_schema.py              # Shared base schema
│   │   ├── auth_schema.py              # Register / Login request + response
│   │   ├── db_connection_schema.py     # Connection request + response schemas
│   │   └── chat_schema.py              # Session + message request + response
│   │
│   ├── services/
│   │   ├── auth_service.py             # Registration & login business logic
│   │   ├── db_connection_service.py    # Connection + schema orchestration
│   │   └── chat_service.py             # NL → SQL → execute → answer pipeline
│   │
│   └── utils/
│       ├── enums.py                    # UserRole, Permission, DbType, LlmMode…
│       ├── schema_extractor.py         # SQLAlchemy inspector → schema dict
│       ├── sql_cleaner.py              # Strip markdown/fences from LLM output
│       └── sql_validator.py            # Detect SQL operation type (SELECT, INSERT…)
│
└── db_migrations/
    ├── env.py                          # Alembic environment (auto-discovers models)
    ├── script.py.mako                  # Migration file template
    └── versions/                       # Migration history files
```

---

## Architecture & Request Flow

### Natural Language to SQL Pipeline

This is the core flow that runs every time a user sends a message:

1. User sends a natural-language question to `POST /api/v1/chat/message`
2. JWT dependency extracts user identity and permission level
3. `ChatService` retrieves the chat session → DB connection → cached schema snapshot
4. Last N messages are fetched to build conversation history context
5. `PromptBuilder` assembles the SQL generation prompt: schema + history + question
6. `LLMFactory` selects the correct LLM backend (Gemini or Ollama) based on session mode
7. LLM generates a SQL query; `SQLCleaner` strips any markdown formatting/fences
8. `QueryGuard` validates the SQL operation type against the user's permission level
9. `EngineCreator` builds a SQLAlchemy engine to the user's target database
10. Query is executed; result rows are serialized (dates, Decimals handled)
11. LLM receives the original question + result rows and generates a natural-language answer
12. Both the user message and assistant response are persisted to chat history
13. Full `MessageResponse` (SQL, result, answer, execution time) is returned to the client

### LLM Abstraction

All LLM clients implement `BaseLLM` with three methods: `generate_sql()`, `generate_answer()`, and `generate_title()`. `LLMFactory.get_llm(mode)` returns the appropriate implementation based on the `LlmMode` enum (`local` | `online`) stored per chat session. Adding a new LLM provider only requires implementing `BaseLLM` and registering it in the factory.

### Permission Model

| Role | Permission Level | Allowed SQL Operations |
|---|---|---|
| `viewer` | `SELECT_ONLY` | SELECT |
| `analyst` | `READ_WRITE` | SELECT, INSERT |
| `admin` | `ADMIN_ACCESS` | SELECT, INSERT, UPDATE, DELETE, ALTER, DROP |

---

## Backend — Installation & Setup Guide

### Prerequisites

- Python 3.13 or higher
- PostgreSQL 14+ (running locally or accessible remotely)
- `pip` and `venv`
- Google Gemini API key (if using online mode)
- Ollama installed locally (if using local mode) — see [Local Model Setup](#local-model-setup-ollama--qwen25) below

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-org/schema-mind-backend.git
cd schema-mind-backend
```

### Step 2 — Create & Activate a Virtual Environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Generate the Fernet Encryption Key

Database passwords are stored encrypted. Generate a key before configuring the environment:

```bash
python generate_key.py
# Output example: b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx='
# Copy this value — you will need it for DB_CREDENTIAL_ENCRYPTION_KEY below
```

> **Never commit your `.env` file or the generated key to version control.** Add `.env` to your `.gitignore`.

### Step 5 — Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

| Variable | Example Value | Notes |
|---|---|---|
| `SECRET_KEY` | `your-random-secret` | JWT signing key — use a long random string |
| `DB_CREDENTIAL_ENCRYPTION_KEY` | output from `generate_key.py` | Fernet key for encrypting DB passwords |
| `POSTGRES_USER` | `postgres` | Application DB user |
| `POSTGRES_PASSWORD` | `your-pg-password` | Application DB password |
| `POSTGRES_DB` | `schema_mind_db` | Application DB name (must exist) |
| `POSTGRES_HOST` | `localhost` | Application DB host |
| `POSTGRES_PORT` | `5432` | Application DB port |
| `GEMINI_API_KEY` | `AIza...` | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Model tag pulled in Ollama |
| `OLLAMA_TIMEOUT` | `60` | Request timeout in seconds |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins (JSON array string) |

### Step 6 — Create the Application Database

```sql
psql -U postgres
CREATE DATABASE schema_mind_db;
\q
```

### Step 7 — Run Alembic Migrations

This creates all required tables (`users`, `db_connections`, `schema_cache`, `chat_sessions`, `chat_messages`, `audit_logs`):

```bash
alembic upgrade head
```

### Step 8 — Start the Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now running at `http://localhost:8000`.
Swagger UI (interactive docs) is available at `http://localhost:8000/docs`.
ReDoc is available at `http://localhost:8000/redoc`.

---

## Local Model Setup (Ollama + qwen2.5)

SchemaMind supports fully offline operation using Ollama. This section explains how to install Ollama, pull the recommended model, and configure the backend to use it.

### What is Ollama?

Ollama is a tool for running large language models locally on your machine. It exposes an HTTP API (default: `http://localhost:11434`) that SchemaMind's `OllamaClient` calls directly — no internet connection required after the model is downloaded.

### Step 1 — Install Ollama

**macOS**
```bash
brew install ollama
```

**Linux**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows**
Download the installer from [https://ollama.com](https://ollama.com) and run it. Ollama will be available as a system service.

### Step 2 — Start the Ollama Server

```bash
ollama serve
# Ollama listens on http://localhost:11434 by default
```

On macOS and Windows the Ollama application starts the server automatically. On Linux, enable it as a service:

```bash
sudo systemctl enable --now ollama
```

### Step 3 — Pull the Recommended Model

SchemaMind defaults to `qwen2.5:3b`, a compact but capable model well-suited for SQL generation on consumer hardware:

```bash
ollama pull qwen2.5:3b

# Verify the model is available
ollama list
```

> `qwen2.5:3b` requires approximately 2.3 GB of disk space and runs comfortably on a machine with 8 GB RAM. For higher accuracy on complex schemas, try `qwen2.5:7b` (~4.7 GB) or `qwen2.5:14b` (~9 GB) and update `OLLAMA_MODEL` in your `.env` accordingly.

### Step 4 — Verify the Connection

Test that Ollama is reachable before starting SchemaMind:

```bash
curl http://localhost:11434/api/generate \
  -d '{"model": "qwen2.5:3b", "prompt": "SELECT 1", "stream": false}'
```

You should receive a JSON response with a `response` field containing a SQL string.

### Step 5 — Configure the Backend

Ensure your `.env` contains:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:3b
OLLAMA_TIMEOUT=60
```

### Using Local Mode in a Chat Session

When creating a chat session via the API, set `llm_mode` to `"local"`:

```json
POST /api/v1/chat/session
{
  "db_connection_id": 1,
  "llm_mode": "local"
}
```

Set `llm_mode` to `"online"` to use Google Gemini instead. The mode is stored per-session, so you can run different sessions with different backends simultaneously.

---

## API Endpoints Summary

### Authentication — `/api/v1/auth`

| Method + Path | Auth | Description |
|---|---|---|
| `POST /register` | None | Register a new user; returns a JWT access token |
| `POST /login` | None | Authenticate with email/password; returns a JWT access token |

### Database Connections — `/api/v1/connections`

| Method + Path | Auth | Description |
|---|---|---|
| `GET /` | JWT | List all DB connections for the authenticated user |
| `POST /` | JWT | Add a new connection; auto-extracts and caches the schema |
| `PUT /` | JWT | Update connection details |
| `DELETE /{id}` | JWT | Remove a connection (cascades to sessions & messages) |
| `GET /{id}/schema` | JWT | Retrieve the cached schema snapshot |
| `POST /schema/refresh` | JWT | Re-extract the schema from the target database |

### Chat — `/api/v1/chat`

| Method + Path | Auth | Description |
|---|---|---|
| `GET /sessions` | JWT | List all chat sessions for the user + connection |
| `GET /sessions/{id}` | JWT | Get a single session by ID |
| `POST /session` | JWT | Create a new chat session |
| `PUT /session` | JWT | Update session metadata (e.g., rename title) |
| `DELETE /session/{id}` | JWT | Delete a session and all its messages |
| `GET /messages/{session_id}` | JWT | Retrieve full message history for a session |
| `POST /message` | JWT | Send a message — triggers the NL → SQL → execute → answer pipeline |

---

## Roadmap — Version 2

- **Schema Context Optimization via Vector DB (RAG)** — Instead of injecting the full schema into every prompt, relevant tables and columns will be retrieved using semantic similarity search. This will dramatically reduce token usage for large schemas and improve query accuracy on complex databases.
- Support for Oracle and SQL Server — `engine_creator` stubs are already in place
- Streaming responses — stream LLM answer tokens to the frontend via SSE
- Query result caching — skip re-execution for identical repeated queries
- Fine-grained audit logging — the `AuditLog` model is already defined in the schema

---

## License

This project is licensed under the MIT License. See the `LICENSE` file in the repository root for details.