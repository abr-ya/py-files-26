# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based file upload service with authentication, SQLite metadata storage, and filesystem blob storage. The server provides:

- User authentication with JWT tokens
- Multipart file upload with size limits (default: 1GB per file)
- SQLite database for metadata (users, stored objects, upload sessions)
- Filesystem storage for actual file blobs
- Automatic TTL-based cleanup of expired files (30-day default)
- Browser-based UI for uploading files
- OpenAPI-documented HTTP APIs under `/api/v1`

**Technical Stack**: Python 3.11+, FastAPI, SQLAlchemy/SQLModel, Pydantic v2, passlib[bcrypt], python-jose (JWT), python-multipart

## Code Architecture

### Main Components

1. **FastAPI Server** (`server/src/py_files_server/main.py`)
   - Entry point with application lifespan management
   - Mounts API routes and static file serving
   - Configures database and storage initialization
   - Runs background TTL purge task

2. **Database Models** (`server/src/py_files_server/models/`)
   - `User`: User accounts with login/password_hash
   - `StoredUploadObject`: Metadata for stored files (owner, size, path, expiration)
   - `UploadSession`: Resumable upload sessions (not fully implemented in MVP)

3. **API Routes** (`server/src/py_files_server/api/routes/`)
   - `auth.py`: User registration and login endpoints
   - `objects.py`: File upload endpoint

4. **Services** (`server/src/py_files_server/services/`)
   - `jwt.py`: JWT token creation and validation
   - `password.py`: Password hashing and verification
   - `fs_storage.py`: Filesystem storage utilities
   - `purge.py`: TTL-based cleanup of expired files

5. **Frontend** (`frontend/`)
   - Basic HTML/JS UI for file uploads
   - Static files served from `/static` route

### Key Data Flow

1. User registers/logs in via `/auth/register` or `/auth/login`
2. Server returns JWT token for authenticated requests
3. User uploads file via `POST /api/v1/objects` with multipart form data
4. File is streamed to disk with size validation
5. Metadata is stored in SQLite database
6. Files automatically expire based on `RETENTION_DAYS` setting
7. Background task periodically purges expired files

## Development Commands

### Setup and Installation

```bash
cd server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"    # For development with test tools
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn py_files_server.main:app --reload

# Production mode
uvicorn py_files_server.main:app --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
cd server
pytest                          # Run all tests
pytest tests/test_objects_upload.py  # Run specific test file
pytest -v                       # Verbose output
pytest --lf                     # Run only last failed tests
```

### Environment Configuration

Key environment variables (can be set in `.env` file in `server/` directory):
- `DATABASE_URL`: SQLite path (default: `sqlite:///./var/py_files.db`)
- `STORAGE_ROOT`: File storage directory (default: `./var/storage`)
- `JWT_SECRET`: Secret key for JWT tokens (change from default in production)
- `MAX_UPLOAD_BYTES`: Maximum file size limit
- `RETENTION_DAYS`: File expiration time

## Project Structure

```
├── server/                     # FastAPI server implementation
│   ├── src/py_files_server/    # Main Python package
│   │   ├── api/                # API routes and schemas
│   │   ├── models/             # Database models
│   │   ├── services/           # Business logic services
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── db.py               # Database setup
│   │   └── settings.py         # Configuration
│   ├── tests/                  # Test suite
│   └── pyproject.toml          # Project dependencies
├── frontend/                   # Browser UI files (served via /static route)
│   ├── templates/              # HTML templates
│   └── static/                 # CSS, JS, images
├── docs/                       # Documentation and specifications
│   └── legacy-specs/           # Feature specs and design documents
│       └── 001-network-file-upload-client/
│           ├── contracts/openapi.yaml  # OpenAPI specification
│           └── plan.md         # Implementation plan and architecture
└── clients/python/             # Future: Python CLI client (planned, not yet implemented)
```

**Important References**:
- OpenAPI contract: `docs/legacy-specs/001-network-file-upload-client/contracts/openapi.yaml`
- Technical context and architecture decisions: `docs/legacy-specs/001-network-file-upload-client/plan.md`

## Testing Approach

Tests use FastAPI's TestClient for integration testing:
- `test_objects_upload.py`: Tests file upload functionality and limits
- `test_health.py`: Basic health check endpoint

Tests can override settings using FastAPI's dependency override mechanism.

## Design Constraints

Per project constitution (see `.cursor/rules/specify-rules.mdc`):
- Use vanilla JavaScript for frontend (no React/Vue frameworks)
- Maintain OpenAPI specification in `docs/legacy-specs/001-network-file-upload-client/contracts/openapi.yaml`
- TLS/HTTPS mandatory for non-localhost deployments
- Single file upload limit: 1GB (1×10⁹ bytes) default
- JWT access token TTL: 24 hours
- Storage backend: filesystem (object store migration deferred until scaling needed)
- Authentication: JWT-based (Google OAuth deferred as optional future enhancement)