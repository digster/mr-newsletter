# Newsletter Manager

A desktop and web application for reading newsletters from your Gmail inbox. Built with Python, Flet, and PostgreSQL.

## Features

- **Gmail Integration**: Connect with your Gmail account via OAuth
- **Label-based Filtering**: Organize newsletters by Gmail labels
- **Auto-fetch**: Automatically fetch new emails at configurable intervals (default: 24 hours)
- **Queue-based Fetching**: Smart queue system with configurable delays between fetches
- **HTML Email Rendering**: View emails with sanitized HTML content
- **Dark/Light Theme**: System-aware theme support
- **Docker Deployment**: Easy deployment with Docker Compose (dev and prod)

## Prerequisites

- Python 3.11+
- [UV](https://docs.astral.sh/uv/) package manager
- PostgreSQL 16+
- Docker & Docker Compose (for containerized deployment)
- Google Cloud Console account

## Google Cloud Console Setup

Before using the app, you need to create OAuth credentials in Google Cloud Console:

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" (or "Internal" for G Suite)
   - Fill in the required fields:
     - App name: "Newsletter Manager" (or your preferred name)
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.labels`
   - Add test users (your Gmail address)

4. **Create OAuth Client ID**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Newsletter Manager Desktop"
   - Click "Create"

5. **Copy Credentials**
   - Copy the **Client ID** and **Client Secret**
   - You'll enter these in the app's Setup page on first launch

## Installation

### Using UV (Recommended)

```bash
# Clone the repository
git clone https://github.com/digster/mr-newsletter.git
cd mr-newsletter

# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Change ENCRYPTION_KEY in production!
```

### Running Locally

1. **Start PostgreSQL** (or use Docker):
   ```bash
   docker run -d \
     --name newsletter-postgres \
     -e POSTGRES_USER=newsletter \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=newsletter \
     -p 5432:5432 \
     postgres:16-alpine
   ```

2. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

3. **Start the application**:
   ```bash
   # Desktop app mode
   uv run python -m src.main

   # Web app mode
   FLET_WEB_APP=true uv run python -m src.main
   ```

4. **Open the app** and complete setup:
   - Enter your Google OAuth Client ID and Client Secret
   - Sign in with your Gmail account
   - Add newsletters by selecting Gmail labels

## Docker Deployment

### Development

```bash
# Start development environment
docker compose -f docker-compose.dev.yml up --build

# Access at http://localhost:8550
```

### Production

```bash
# Create .env file with production settings
cp .env.example .env

# Edit .env with secure values:
# - POSTGRES_PASSWORD: strong password
# - ENCRYPTION_KEY: 32+ character random string

# Start production environment
docker compose up -d --build

# Access at http://localhost:8550
```

## Standalone Build

Create a standalone executable that can be distributed without requiring Python installation.

### Build Command

```bash
# Using Makefile (recommended)
make build

# Or manually
uv run flet pack src/main.py --name "Newsletter Manager"
```

This creates a standalone executable in the `dist/` directory.

### Build Options

| Option | Description |
|--------|-------------|
| `--name "App Name"` | Set the application name |
| `--icon path/to/icon.png` | Set the app icon |
| `--add-data "src:src"` | Include additional data files |
| `--hidden-import module` | Include hidden imports |
| `--product-version "1.0.0"` | Set version number |

### Full Build Example

```bash
uv run flet pack src/main.py \
    --name "Newsletter Manager" \
    --add-data "src/config:src/config" \
    --add-data "src/ui:src/ui" \
    --hidden-import sqlalchemy \
    --hidden-import asyncpg \
    --hidden-import google.auth \
    --hidden-import apscheduler
```

### Platform Output

- **macOS**: Creates a `.app` bundle in `dist/`
- **Windows**: Creates a `.exe` in `dist/`
- **Linux**: Creates an executable binary in `dist/`

### Troubleshooting Builds

If you encounter missing module errors at runtime, add them via `--hidden-import`. SQLAlchemy and Google API libraries often need explicit inclusion.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Runtime environment (development/production) | development |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql+asyncpg://... |
| `POSTGRES_PASSWORD` | PostgreSQL password (Docker) | - |
| `ENCRYPTION_KEY` | Key for encrypting credentials in DB | - |
| `FLET_HOST` | Host to bind to | 127.0.0.1 |
| `FLET_PORT` | Port to listen on | 8550 |
| `FLET_WEB_APP` | Run as web app (true/false) | false |
| `DEFAULT_FETCH_INTERVAL` | Default fetch interval in minutes | 1440 |
| `FETCH_QUEUE_DELAY_SECONDS` | Delay between newsletter fetches | 5 |
| `LOG_LEVEL` | Logging level | INFO |

## Usage

### Adding Newsletters

1. Click "Manage Newsletters" or the folder icon
2. Click the "+" button
3. Enter a name for the newsletter
4. Select the Gmail label used to filter these emails
5. Configure auto-fetch settings
6. Click "Add"

### Reading Emails

1. Click on a newsletter card to see its emails
2. Click on an email to read it
3. Use the star button to mark favorites
4. Use archive to hide read emails

### Manual Refresh

- Click the refresh icon on a newsletter card for individual refresh
- Click the global refresh icon to queue all newsletters

## Project Structure

```
mr-newsletter/
├── src/
│   ├── main.py              # Entry point
│   ├── app.py               # Main Flet app
│   ├── config/              # Configuration
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   ├── repositories/        # Data access
│   ├── ui/                  # UI components and pages
│   └── utils/               # Utilities
├── migrations/              # Alembic migrations
├── tests/                   # Test suite
├── docker/                  # Docker files
├── docker-compose.yml       # Production compose
├── docker-compose.dev.yml   # Development compose
└── pyproject.toml           # Project configuration
```

## Development

### Makefile Commands

The project includes a Makefile for common tasks:

```bash
make help       # Show all available commands
make install    # Install dependencies
make run        # Run desktop app
make run-web    # Run web app
make build      # Create standalone executable
make test       # Run tests
make lint       # Run linter
make format     # Format code
make typecheck  # Run type checker
make migrate    # Run database migrations
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_services/test_newsletter_service.py
```

### Creating Migrations

```bash
# Generate a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Rollback last migration
uv run alembic downgrade -1
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

## Security Notes

- OAuth credentials (both client secrets and user tokens) are stored encrypted in PostgreSQL
- The `ENCRYPTION_KEY` environment variable is used for encryption
- **Never commit `.env` files or expose your encryption key**
- In production, use a strong, unique encryption key (32+ characters)

## Troubleshooting

### OAuth Errors

- Ensure Gmail API is enabled in Google Cloud Console
- Verify your email is added as a test user
- Check that scopes are correctly configured

### Database Connection Issues

- Verify PostgreSQL is running
- Check DATABASE_URL format
- Ensure database exists and user has permissions

### Fetch Not Working

- Check that auto-fetch is enabled for the newsletter
- Verify Gmail label exists and has emails
- Check logs for API errors

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request
