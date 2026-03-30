# Construction Site Management System

A FastAPI-based backend for managing construction sites, labor, expenses, and warehouse inventory.

## Features

- **Multi-role system**: Admin, Supervisor, Driver
- **Labor Management**: Worker registration, attendance tracking
- **Site Management**: Site creation, assignment, expense tracking
- **Warehouse Management**: Inventory tracking, stock movements
- **Auto-expense Calculation**: Automatic expense generation from warehouse transfers (R001-R002)
- **Financial Tracking**: Site accounts, daily balances, purchase records

## Quick Start

### 1. Setup Environment

```
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```
### 2. Setup Database
```
# Create database
createdb construction_db  # PostgreSQL

# Run migrations
alembic upgrade head
```
### 3. Run Development Server
```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Access API docs at: http://localhost:8000/docs
```
## Project Structure

```
csms-backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/              # API routes
│   ├── core/             # Security, exceptions
│   ├── crud/             # Database operations
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (R001-R006)
│   └── main.py           # Application entry
└── tests/                # Test suite
```
## Business Rules Implementation
| Rule | Description                      | Location                         |
| ---- | -------------------------------- | -------------------------------- |
| R001 | Stock movement auto-expense      | `services/expense_calculator.py` |
| R002 | Purchase-based price calculation | `services/expense_calculator.py` |
| R003 | Driver bata calculation          | `services/` (TODO)               |
| R004 | Site account balance check       | `services/site_account.py`       |
| R005 | Attendance date validation       | `services/attendance_service.py` |
| R006 | Site-assignment validation       | `services/attendance_service.py` |


## API Endpoints

#### Authentication
- POST /api/v1/auth/login - OAuth2 login
#### Users (Admin only)
- GET /api/v1/users/ - List users
- POST /api/v1/users/ - Create user
- GET /api/v1/users/me - Current user profile

## Development
#### Run Tests
```
pytest
```

#### Code Formatting
```
black app/ tests/
isort app/ tests/
```

#### Database Migrations
```
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

License
 	Private - All rights reserved