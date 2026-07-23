# Child DNA Backend API

Powered by REUNITE AI

## Project Architecture

This backend follows Clean Architecture principles with a modular structure:

```
backend/
├── app/                    # Application code
│   ├── api/               # API routes and versioning
│   ├── core/              # Core configuration and constants
│   ├── config/            # Pydantic settings
│   ├── database/          # SQLAlchemy engine and session
│   ├── middleware/        # Custom middleware
│   ├── routers/           # API endpoint routers
│   ├── security/          # JWT and authentication utilities
│   └── utils/             # Helper utilities
├── tests/                 # Test suite
├── alembic/              # Database migrations
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
└── docker-compose.yml    # Container orchestration
```

## Folder Structure

| Directory | Purpose |
|-----------|---------|
| `app/api/v1/` | API v1 router aggregation |
| `app/core/` | Application constants and lifespan events |
| `app/config/` | Pydantic settings for environment variables |
| `app/database/` | SQLAlchemy engine and session management |
| `app/middleware/` | CORS and logging middleware |
| `app/routers/system/` | System endpoints (health check) |
| `app/security/` | JWT utilities and authentication helpers |
| `app/utils/` | Logging and exception utilities |
| `tests/` | Pytest test suite |
| `alembic/` | Database migration scripts |

## Environment Setup

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker (optional)

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from template:
```bash
cp .env.example .env
```

4. Update `.env` with your configuration:
```bash
# Edit .env with your database URL and secret key
```

5. Run the application:
```bash
uvicorn main:app --reload
```

## Docker Setup

1. Build and start containers:
```bash
docker-compose up --build
```

2. The API will be available at:
```
http://localhost:8000
```

3. PostgreSQL will be available at:
```
localhost:5432
```

## API Documentation

### Swagger UI
Access the interactive API documentation at:
```
http://localhost:8000/docs
```

### ReDoc
Alternative API documentation at:
```
http://localhost:8000/redoc
```

### Health Check Endpoint
```
GET /api/v1/system/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

## Development Workflow

### Running Tests
```bash
pytest tests/ -v
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting
```bash
# Install development tools
pip install black isort flake8

# Format code
black app/
isort app/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Child DNA API" |
| `APP_VERSION` | API version | "1.0.0" |
| `DEBUG` | Debug mode | false |
| `DATABASE_URL` | PostgreSQL connection string | - |
| `JWT_SECRET_KEY` | Secret for JWT signing | - |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | 30 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | 7 |
| `CORS_ORIGINS` | Allowed CORS origins | - |
| `LOG_LEVEL` | Logging level | INFO |

## Security Considerations

- All sensitive data is loaded from environment variables
- JWT tokens use HS256 algorithm with secure secret
- Passwords are hashed using bcrypt
- CORS is configured to allow only specified origins
- All requests are logged for audit purposes

## License

Proprietary - Child DNA Platform