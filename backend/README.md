# Backend Architecture Overview

This demo backend is built with FastAPI and provides REST API endpoints for CRUD operations and analytics for a simplified PnL tracking application. Below is an overview of the folder structure and the purpose of each component.

### Azure Hosting link:  https://fastapi-backend-2.azurewebsites.net/docs
Note that they are hosted on free-tier, so there can be a bootup time of 30-45 seconds due to cold starts.

## Folder Structure

```
backend/
├── run_api.py           # Entry point to start the FastAPI server
├── Dockerfile           # Containerization setup
├── database/
│   └── portfolio_data.sqlite   # SQLite database file
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI app instantiation and route inclusion
│   │   ├── config.py            # API configuration and settings
│   │   ├── dependencies.py      # Dependency injection for routes
│   │   ├── utils.py             # API utility functions
│   │   ├── routers/
│   │   │   ├── pnl.py           # PnL (Profit & Loss) API endpoints
│   │   │   ├── trades.py        # Trade data API endpoints
│   │   │   └── prices.py        # Price data API endpoints
│   │   └── middleware/
│   │       ├── logging.py           # Request/response logging middleware
│   │       ├── exception_handling.py # Custom exception handling
│   │       └── auth_handling.py      # Authentication/authorization middleware
│   ├── analytics/
│   │   └── pnl_analytics.py     # Core logic for PnL analytics and calculations
│   ├── data_acess/
│   │   ├── repository.py        # Database access and query logic
│   │   └── db_schema/
│   │       └── trade_data.py    # ORM/data model for trade data
│   └── utils/
├── tests/
│   ├── api/                    # Tests for API endpoints and routers
│   ├── analytics/              # Tests for analytics logic
│   └── data_access/            # Tests for data access layer
└── __init__.py
```

## Key Components

- **api/**: Main FastAPI application code, including routers for different endpoints and middleware for logging, error handling, and authentication.
- **analytics/**: Contains business logic for analytics, especially PnL calculations.
- **data_acess/**: Data access layer for database operations.
- **database/**: Contains the SQLite database file for persistent storage.
- **tests/**: Unit and integration tests for all backend modules.

## Running the Backend

```bash
# From the backend directory
uvicorn src.api.main:app --reload
```

Or use the provided `run_api.py` script.

## Notes
- The backend is modular, separating API, analytics, and data access for maintainability.
- All business logic and database access are abstracted from the API layer.
- Middleware is used for logging, error handling, and authentication. 