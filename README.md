# Mini-CRM "Repair Requests"

## Links

**Repository:** https://github.com/Mir1a/test_project

**Docker Hub:** https://hub.docker.com/r/m1ria/test_project

**Image:** `m1ria/test_project:latest`

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Run Application

1. Clone repository:
```bash
git clone https://github.com/Mir1a/test_project.git
cd test_project
```

2. Create `.env` file:
```env
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=mydb
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Start services:
```bash
docker-compose up -d
```

Application will be available at:
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Adminer: http://localhost:8080

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DB_HOST | PostgreSQL host | db |
| DB_PORT | PostgreSQL port | 5432 |
| DB_USER | Database user | postgres |
| DB_PASS | Database password | - |
| DB_NAME | Database name | mydb |
| SECRET_KEY | Application secret key | - |
| JWT_SECRET_KEY | JWT signing key | - |
| JWT_ALGORITHM | JWT algorithm | HS256 |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | Access token expiration time (minutes) | 30 |

## Migrations

Migrations run automatically on container startup via `entrypoint.sh`

Manual migration:
```bash
docker-compose exec app alembic upgrade head
```

## Test Accounts

### Admin
```
Email: admin@example.com
Password: admin123
```

### Worker
```
Email: worker@example.com
Password: worker123
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info

### Public (Client)
- `POST /client/tickets` - Create repair request (no auth required)

### Admin Only
- `GET /tickets` - List all tickets (pagination, search, filters)
- `PATCH /tickets/{id}/assign` - Assign ticket to worker
- `DELETE /tickets/{id}/assign` - Unassign worker from ticket
- `GET /users` - List all users
- `GET /users/{id}` - Get user details
- `POST /users` - Create new user
- `PUT /users/{id}` - Full update user
- `PATCH /users/{id}` - Partial update user
- `DELETE /users/{id}` - Delete user

### Worker Only
- `GET /tickets/my` - List assigned tickets
- `PATCH /tickets/{id}/status` - Update ticket status

### Query Parameters
- `skip` - Number of items to skip (default: 0)
- `limit` - Items per page (default: 10, max: 100)
- `search` - Search by ticket title
- `status` - Filter by status (new, in_progress, done)

## Tech Stack

- Python 3.13
- FastAPI
- Pydantic 2.0+
- SQLAlchemy 2.0 (async)
- PostgreSQL 15
- Alembic
- JWT authentication
- Docker & Docker Compose

## CI/CD

GitHub Actions configured to automatically:
- Build and push Docker image on push to `main`
- Tag and push on version tags (`v*`)
