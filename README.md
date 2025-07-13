# FastAPI Streamlit Trading Dashboard

A full-stack application with a FastAPI backend and Streamlit frontend for trade data and PnL tracking.

### Azure Hosted API endpoints:  https://fastapi-backend-2.azurewebsites.net/docs
### Streamlit Application link:  https://streamlit-fronend-1.azurewebsites.net/

Note that they are hosted on free-tier, There can be a bootup time of 30-45 seconds due to cold starts.

## Backend Component (FastAPI)

The backend is a RESTful API built with FastAPI that provides CRUD end points for data management and PnL analytics.

### Backend Architecture
- Modular design with separated API, analytics, and data access layers
- Middleware for logging, error handling, and authentication
- Test suite covering API endpoints, analytics, and data access
- Containerized deployment with Docker in Azure App services

### Core Features
- **CRUD Operations**: Create, Read, Update, Delete functionality for stock prices and trade data
- **PnL Analytics**: P&L analytics time series
- **Data Management**: File upload support using CSV formatted files.
- **Database Integration**: SQLite database with ORM models for persistent storage
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

### API Endpoints
- **Prices API**: `/api/v1/prices` - Stock price data management
- **Trades API**: `/api/v1/trades` - Trading data operations
- **PnL History**: `/api/v1/pnl_history` - Profit and loss analytics
- **File Upload**: `/api/v1/prices/upload`, `/api/v1/trades/upload` - CSV data import
- **Data Deletion**: `/api/v1/prices/{ticker}`, `/api/v1/trades/{ticker}` - Ticker-specific data removal


## Frontend Component (Streamlit)

The frontend is built with Streamlit that provides interface for stock prices, trade data and visualizations for PnL

### Frontend Architecture
- Modular design with separated pages, components, and services layers
- Centralized API client for backend communication and error handling
- Component-based UI with reusable chart and table components
- Containerized deployment with Docker in Azure App services

### Features
- **Multi-tab Interface for Data management**: Tabs are Organized based on CRUD operations.
- **Visualizations**: Plotly-based charts and AG Grid tables
- **File Management**: CSV upload and export capabilities

### Key Pages
- **Data Management**: 
  - Stock Prices tab with data tables and export functionality
  - Trade Data tab with data tables and export functionality
  - Upload Data tab from a CSV file(s)
  - Delete Data tab for ticker-specific data removal

- **PnL Summary**:
  - PnL History table with time series analysis
  - Per-stock PnL analysis with dropdown selection

## System Integration

The application follows a clean separation of concerns:
- **Backend**: Handles all business logic, data processing, and API endpoints
- **Frontend**: Provides user interface and data visualization
- **Database**: SQLite for data persistence (replacable with another database/datasource)
- **Deployment**: Both components are containerized and hosted on Azure using GitHub actions



## Folder Structure of backend application

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

## Folder Architecture of frontend application

```
frontend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── .streamlit/            # Streamlit configuration
├── src/                   # Source code directory
│   ├── components/        # Reusable UI components
│   │   ├── charts.py      # Chart visualization components
│   ├── pages/             # Page-specific modules
│   │   ├── data_management.py  # Data CRUD operations and management
│   │   └── pnl_summary.py      # PnL analysis and reporting
│   ├── services/          # External service integrations
│   │   └── api_client.py  # API endpoint interactions and HTTP client
│   └── utils/             # Utility modules
│       └── constants.py   # Application constants and configuration
└── tests/                 # Test suite
    ├── test_api_client.py # API client tests
    └── test_components.py # Component tests
```

## Development Tools

**Package Management/Virtual Environments**: UV

**Code Linting, Formatting**: iSort, Black, UV Ruff

**Testing**: PyTest

**Type Checking**: MyPy