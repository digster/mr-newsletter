# Newsletter Manager - Architecture Overview

## Executive Summary

**Newsletter Manager** is a dual-mode (desktop/web) application for reading and organizing Gmail newsletters. It uses Flet for UI, SQLAlchemy for ORM, and implements a sophisticated background task system with priority-based fetch queuing.

**Key distinction**: Desktop mode uses SQLite (no setup required), while web mode uses PostgreSQL. The application maintains encrypted OAuth credentials and never deletes emails from Gmail.

---

## 1. Project Structure & Entry Points

```
mr-newsletter/
├── src/                          # Main application code
│   ├── main.py                  # CLI entry point (bootstraps Flet)
│   ├── app.py                   # NewsletterApp orchestrator
│   ├── config/                  # Configuration management
│   │   └── settings.py          # Pydantic Settings (environment config)
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── base.py             # Base model, async session/engine setup
│   │   ├── newsletter.py        # Newsletter subscriptions
│   │   ├── email.py             # Email storage/metadata
│   │   ├── user_credential.py   # Encrypted OAuth tokens
│   │   └── user_settings.py     # User app preferences
│   ├── services/                # Business logic layer
│   │   ├── auth_service.py      # Gmail OAuth flow, credential storage
│   │   ├── gmail_service.py     # Gmail API client
│   │   ├── newsletter_service.py # Core newsletter operations
│   │   ├── scheduler_service.py # APScheduler wrapper (scheduled fetches)
│   │   └── fetch_queue_service.py # Priority queue for fetches
│   ├── repositories/            # Data access layer
│   │   ├── base_repository.py   # Generic CRUD operations
│   │   ├── newsletter_repository.py
│   │   └── email_repository.py
│   ├── ui/                      # Flet UI layer
│   │   ├── pages/               # Full-page views
│   │   │   ├── login_page.py    # OAuth flow UI
│   │   │   ├── home_page.py     # Dashboard with sidebar
│   │   │   ├── newsletters_page.py # Manage newsletters
│   │   │   ├── email_list_page.py  # Emails for one newsletter
│   │   │   ├── email_reader_page.py # Email content viewer
│   │   │   └── settings_page.py # User preferences
│   │   ├── components/          # Reusable UI widgets
│   │   ├── router.py            # Route navigation helper
│   │   └── themes/              # Design tokens
│   ├── utils/                   # Utilities
│   │   ├── encryption.py        # Fernet-based encryption
│   │   └── html_sanitizer.py    # Email HTML sanitization
│   └── __init__.py
├── migrations/                  # Alembic database migrations
│   ├── env.py                   # Migration environment config
│   ├── script.py.mako           # Migration template
│   └── versions/                # Individual migration files
├── tests/                       # Test suite (unit + E2E)
├── docker/                      # Docker configuration
│   ├── Dockerfile               # Production image
│   └── compose files
├── scripts/                     # Utility scripts
├── pyproject.toml               # Project metadata & dependencies
└── alembic.ini                  # Alembic config
```

### Entry Points

1. **Desktop Mode**: `python -m src.main` → Uses SQLite, opens native Flet window
2. **Web Mode**: `FLET_WEB_APP=true python -m src.main` → Uses PostgreSQL, opens browser at `http://127.0.0.1:8550`
3. **Docker**: `docker compose up` → Web mode with PostgreSQL in container

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                              UI Layer                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Login   │ │   Home   │ │ Newslet- │ │  Email   │ │ Settings │  │
│  │   Page   │ │   Page   │ │ters Page │ │  Reader  │ │   Page   │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       │            │            │            │            │         │
│       └────────────┴────────────┴────────────┴────────────┘         │
│                              ▼                                       │
├─────────────────────────────────────────────────────────────────────┤
│                         Service Layer                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │ AuthService  │ │ GmailService │ │ Newsletter   │                 │
│  │ (OAuth)      │ │ (API Client) │ │ Service      │                 │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                 │
│         │                │                │                          │
│  ┌──────┴────────────────┴────────────────┴───────┐                 │
│  │              Background Services               │                 │
│  │  ┌──────────────────┐  ┌───────────────────┐  │                 │
│  │  │ SchedulerService │  │ FetchQueueService │  │                 │
│  │  │ (APScheduler)    │  │ (Priority Queue)  │  │                 │
│  │  └──────────────────┘  └───────────────────┘  │                 │
│  └────────────────────────────────────────────────┘                 │
├─────────────────────────────────────────────────────────────────────┤
│                       Repository Layer                               │
│  ┌──────────────────┐  ┌──────────────────┐                         │
│  │ NewsletterRepo   │  │   EmailRepo      │                         │
│  └────────┬─────────┘  └────────┬─────────┘                         │
│           │                     │                                    │
│           └──────────┬──────────┘                                    │
│                      ▼                                               │
├─────────────────────────────────────────────────────────────────────┤
│                         ORM Layer                                    │
│                   SQLAlchemy 2.0 (Async)                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │Newsletter│ │  Email   │ │UserCred  │ │UserSett- │               │
│  │  Model   │ │  Model   │ │  Model   │ │ings Model│               │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘               │
├─────────────────────────────────────────────────────────────────────┤
│                       Database Layer                                 │
│         SQLite (Desktop)  │  PostgreSQL (Web)                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components & Relationships

### Application Orchestrator (`src/app.py`)

The `NewsletterApp` class is the central orchestrator:

```
NewsletterApp
├── Page (Flet)
├── Services (initialized on demand)
│   ├── AuthService → Database sessions
│   ├── GmailService → OAuth credentials
│   ├── NewsletterService → Business logic
│   ├── SchedulerService → Background jobs (APScheduler)
│   └── FetchQueueService → Priority queue processor
├── Database (async engine + session maker)
└── Routing (page navigation)
```

**Key responsibilities**:
- Initialize database connection (SQLite or PostgreSQL based on mode)
- Check auth status and route to login or home
- Manage service lifecycle
- Handle page routing and navigation

---

## 4. Data Models & Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│ UserCredential  │ (1:1 with user, encrypted tokens)
│  - user_email   │
│  - access_token │ (encrypted)
│  - refresh_token│ (encrypted, nullable)
│  - token_expiry │
└─────────────────┘

┌──────────────────────┐      ┌────────────────────────┐
│ Newsletter           │ 1─N  │ Email                  │
│ (subscription)       ├─────→│ (stored email)         │
│                      │      │                        │
│ - name               │      │ - gmail_message_id     │
│ - gmail_label_id     │      │ - subject              │
│ - auto_fetch_enabled │      │ - sender_email         │
│ - fetch_interval     │      │ - received_at          │
│ - last_fetched_at    │      │ - body_html (sanitized)│
│ - unread_count       │      │ - is_read              │
│ - total_count        │      │ - is_starred           │
│ - is_active          │      │ - is_archived          │
└──────────────────────┘      └────────────────────────┘

┌────────────────────┐
│ UserSettings       │ (Singleton, id=1)
│                    │
│ - theme_mode       │
│ - accent_color     │
│ - global_auto_fetch│
│ - user_email       │ (cached from OAuth)
│ - user_name        │
└────────────────────┘
```

### Key Models

| Model | File | Purpose |
|-------|------|---------|
| **Newsletter** | `src/models/newsletter.py` | Links Gmail label to app newsletter, tracks fetch metadata |
| **Email** | `src/models/email.py` | Stores email metadata, sanitized HTML, and AI summaries |
| **UserCredential** | `src/models/user_credential.py` | OAuth tokens encrypted with Fernet |
| **UserSettings** | `src/models/user_settings.py` | Singleton for UI preferences |

### Database Configuration

| Mode | Driver | Connection String Pattern |
|------|--------|---------------------------|
| Desktop | aiosqlite | `sqlite+aiosqlite:///{app_data_dir}/newsletter.db` |
| Web | asyncpg | `postgresql+asyncpg://user:pass@host:5432/newsletter` |

---

## 5. Services & Their Responsibilities

### AuthService (`src/services/auth_service.py`)

**Purpose**: Manage OAuth flow and credential storage

| Method | Description |
|--------|-------------|
| `start_oauth_flow()` | Initiate Google OAuth (opens browser) |
| `get_user_credentials()` | Retrieve and refresh tokens |
| `logout()` | Clear credentials |

**Security**: Tokens encrypted with Fernet (AES-128-CBC) before storage

---

### GmailService (`src/services/gmail_service.py`)

**Purpose**: Wrapper around Google Gmail API client

| Method | Description |
|--------|-------------|
| `get_user_email()` | Get authenticated user's email |
| `get_labels()` | Fetch all/user-only labels |
| `get_messages()` | Fetch messages by label |
| `get_message_content()` | Get full message body |

---

### NewsletterService (`src/services/newsletter_service.py`)

**Purpose**: Business logic for newsletter operations

| Method | Description |
|--------|-------------|
| `create_newsletter()` | Create subscription |
| `fetch_newsletter_emails()` | Sync emails from Gmail to DB |
| `get_emails_for_newsletter()` | Paginated email listing |
| `mark_email_read/starred/archived()` | Update email status |

---

### SchedulerService (`src/services/scheduler_service.py`)

**Purpose**: Background scheduler for periodic fetches (APScheduler)

| Method | Description |
|--------|-------------|
| `schedule_newsletter_fetch()` | Add interval job |
| `unschedule_newsletter_fetch()` | Remove job |
| `update_newsletter_schedule()` | Reschedule on user change |

---

### FetchQueueService (`src/services/fetch_queue_service.py`)

**Purpose**: Priority-based queue to manage fetch operations with backpressure

**Priority Levels**:
- `HIGH` (1) = manual refresh (runs first)
- `NORMAL` (2) = scheduled fetch
- `LOW` (3) = background fetch

**Prevents Gmail API rate limiting** by introducing configurable delays between fetches.

---

### LLMService (`src/services/llm_service.py`)

**Purpose**: AI-powered email summarization using OpenAI-compatible APIs

| Method | Description |
|--------|-------------|
| `summarize_email()` | Generate concise summary for an email |
| `check_connection()` | Test connectivity to LLM API |
| `is_enabled()` | Check if summarization is enabled |

**Configuration Priority**: UserSettings (DB) → Environment variables → Defaults

**Compatible APIs**: LM Studio, Ollama, OpenAI, or any OpenAI-compatible endpoint

---

## 6. UI Structure

### Routing

| Route | Page | Description |
|-------|------|-------------|
| `/config-error` | ConfigErrorView | Missing OAuth credentials |
| `/login` | LoginPage | OAuth flow UI |
| `/home` | HomePage | Dashboard with sidebar |
| `/newsletters` | NewslettersPage | Manage subscriptions |
| `/newsletter/{id}` | EmailListPage | Emails for one newsletter |
| `/email/{id}` | EmailReaderPage | Full email content |
| `/settings` | SettingsPage | User preferences |

### Component Organization

- **Pages** (`src/ui/pages/`): Full-screen views inheriting from `ft.View`
- **Components** (`src/ui/components/`): Reusable widgets (cards, dialogs, lists)
- **Themes** (`src/ui/themes/`): Centralized design tokens

### Design System (`src/ui/themes/design_tokens.py`)

Inspired by Linear, Notion, and Stripe:
- **Spacing**: 4px grid (XXS=4 → XXL=48)
- **Typography**: H1-H4, Body, Caption with weights
- **Colors**: Slate palette + blue accent, semantic colors
- **Shadows**: Layered elevation system

---

## 7. Configuration Management

### Settings (`src/config/settings.py`)

Pydantic Settings model loading from `.env`:

| Category | Variables |
|----------|-----------|
| **Environment** | `ENVIRONMENT`, `DEBUG` |
| **Database** | `POSTGRES_DATABASE_URL`, `SQLITE_DB_NAME` |
| **Security** | `ENCRYPTION_KEY` (min 16 chars) |
| **Gmail OAuth** | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| **Flet UI** | `FLET_HOST`, `FLET_PORT`, `FLET_WEB_APP` |
| **Scheduler** | `SCHEDULER_ENABLED`, `DEFAULT_FETCH_INTERVAL`, `FETCH_QUEUE_DELAY_SECONDS` |
| **LLM** | `LLM_ENABLED`, `LLM_API_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_MAX_TOKENS`, `LLM_TEMPERATURE` |

### Platform Data Directory

| Platform | Path |
|----------|------|
| Linux | `~/.local/share/mr-newsletter/` |
| macOS | `~/Library/Application Support/mr-newsletter/` |
| Windows | `%LOCALAPPDATA%/mr-newsletter/` |

---

## 8. External Integrations

### Gmail API

**OAuth Scopes**:
```python
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels"
]
```

**API Calls Used**:
- `users().getProfile()` - Get user email
- `users().labels().list()` - Get all labels
- `users().messages().list()` - List messages by label
- `users().messages().get()` - Get full message content

**Rate Limiting**: Handled by FetchQueueService with configurable delays

---

## 9. Web vs Desktop Mode

| Aspect | Desktop | Web |
|--------|---------|-----|
| **Database** | SQLite (aiosqlite) | PostgreSQL (asyncpg) |
| **Storage** | User app data dir | Database server |
| **Setup** | Automatic | Docker compose or manual |
| **Flet Mode** | Native window | Browser at localhost:8550 |
| **Multi-user** | Single user | Multi-user support |

Mode determined by `FLET_WEB_APP` environment variable.

---

## 10. Data Flows

### Authentication Flow

```
User clicks "Sign in with Google"
    ↓
AuthService.start_oauth_flow()
    ├─ Start local server (random port)
    └─ Open browser to Google OAuth
    ↓
User consents → callback received
    ↓
Encrypt tokens → Store in DB
    ↓
Navigate to /home
```

### Email Fetch Flow

```
User clicks refresh OR scheduled time arrives
    ↓
FetchQueueService.queue_fetch(newsletter_id, priority)
    ↓
Queue processor:
    ├─ Pop next task
    ├─ NewsletterService.fetch_newsletter_emails()
    │   ├─ GmailService.get_messages()
    │   ├─ Sanitize HTML
    │   └─ Upsert to emails table
    ├─ Wait delay_seconds
    └─ Next task
```

---

## 11. Key Patterns & Conventions

### Async-First Architecture
All database operations use AsyncSession for non-blocking I/O.

### Repository Pattern
Data access abstraction: Service → Repository → SQLAlchemy → Database

### Encryption at Rest
OAuth credentials encrypted with Fernet before storage.

### Priority Queue for Fetches
Prevents Gmail API rate limiting with configurable delays.

### Cascade Deletes
Newsletter deletion cascades to emails (local DB only, never Gmail).

### HTML Sanitization
Email HTML sanitized with BeautifulSoup + bleach to prevent XSS.

### Type Safety
Full type hints, Pydantic validation, mypy strict mode.

---

## 12. Critical Developer Workflows

### Setup

```bash
# Install dependencies
uv sync

# Configure Google OAuth
make setup-gcloud  # Interactive wizard

# Copy and edit environment
cp .env.example .env
```

### Development

```bash
make run           # Desktop mode
make run-web       # Web mode
make run-web-debug # Web mode with MCP browser tools
make typecheck     # Type checking
make lint          # Linting
make format        # Formatting
```

### Database

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

### Testing

```bash
make test          # Unit tests
make test-e2e      # E2E tests (visible browser)
make test-e2e-ci   # E2E headless
```

### Deployment

```bash
make build                           # Desktop standalone
docker compose up -d                 # Production web
docker compose -f docker-compose.dev.yml up  # Development web
```

---

## 13. Technology Stack

| Category | Technologies |
|----------|--------------|
| **Frontend** | Flet 0.80.0+, Python 3.11+ |
| **ORM** | SQLAlchemy 2.0.35+, Alembic 1.14.0 |
| **Database Drivers** | asyncpg 0.30.0, aiosqlite 0.20.0 |
| **Scheduler** | APScheduler 3.10.4 |
| **Gmail** | google-api-python-client 2.150.0+, google-auth-oauthlib |
| **Security** | cryptography 43.0.0+ (Fernet) |
| **HTML Processing** | BeautifulSoup4, bleach 6.0.0+ |
| **Config** | Pydantic 2.9.0+, Pydantic-settings, python-dotenv |
| **Testing** | pytest, pytest-asyncio, Playwright |
| **Quality** | ruff, mypy |

---

## 14. Architectural Decisions

1. **No email deletion**: App never deletes from Gmail inbox, only from local DB. Protects user data.

2. **Separate sync from async DB ops**: Email fetch operations run synchronously to prevent SQLite corruption on desktop mode.

3. **Local OAuth callback**: Uses `http://localhost:random_port` for simplicity, no external server needed.

4. **Fernet encryption**: Uses Fernet (AES-128) for credential security with simple key management.

5. **Dual database support**: Single codebase supports SQLite (desktop) and PostgreSQL (web) through abstraction.

6. **Priority-based fetch queue**: Prevents Gmail API rate limiting while keeping UI responsive.

7. **Encrypted credentials at rest**: OAuth tokens always encrypted before storage.

---

## 15. File Organization Conventions

| Directory | Convention |
|-----------|------------|
| `src/models/` | One model per file, TYPE_CHECKING guards for relationships |
| `src/services/` | One service per file, async methods, dataclass return types |
| `src/ui/pages/` | One page per file, inherits `ft.View`, route attribute |
| `src/ui/components/` | Smaller reusable widgets, callback-based state |
| `src/repositories/` | Data access layer, generic CRUD in base |

---

This architecture enables:
- Cross-platform deployment (desktop executable + web)
- Zero-config desktop mode
- Production-grade security (encryption, OAuth)
- Responsive UI (async operations, background queuing)
- Scalability (PostgreSQL for web)
- Developer experience (type safety, testability, clear separation)
