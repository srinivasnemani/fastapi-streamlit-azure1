# Frontend Application

## Overview

A Streamlit-based demo P&L dashboard with visualizations and API integration.

### Azure Hosted API endpoints:  https://fastapi-backend-2.azurewebsites.net/docs
### Streamlit Application link:  https://streamlit-fronend-1.azurewebsites.net/
Note that they are hosted on free-tier, There can be a bootup time of 30-45 seconds due to cold starts.

## Folder Architecture

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

## Core Components

### Main Application (`main.py`)

- Streamlit app configuration and routing
- Page navigation and layout management
- Global state initialization

### API Client (`src/services/api_client.py`)

- **API endpoint interactions** for all backend communication
- HTTP client for FastAPI backend integration
- RESTful CRUD operations (GET, POST, DELETE)
- File upload functionality for CSV data
- Error handling and response processing
- Centralized request management with timeout handling

### Constants (`src/utils/constants.py`)

- Centralized configuration management
- API endpoint definitions
- Application styling constants
- Environment-specific settings

### Chart Components (`src/components/charts.py`)

- Interactive data visualizations
- Plotly-based chart implementations

## Pages and Functionality

### Data Management (`src/pages/data_management.py`)

**Multi-tab interface for comprehensive data operations:**

#### 📈 Stock Prices Tab

- Display stock price data in interactive AG Grid tables
- Refresh functionality with real-time data loading
- CSV export capabilities
- Formatted columns for dollar amounts and percentages
- Date filtering and sorting capabilities

#### 💹 Trade Data Tab

- Trading data visualization with AG Grid
- Real-time data refresh from API
- CSV export functionality
- Interactive charts showing net stocks by ticker
- Position analysis and exposure tracking

#### ☁️ Upload Data Tab

- **File upload functionality** for stock prices and trade data
- CSV file validation and processing
- Progress indicators and success/error messaging
- Support for multiple file formats
- Batch upload capabilities

#### 🗑️ Delete Data Tab

- **Data deletion by ticker** for both prices and trades
- Confirmation dialogs for safe deletion
- Bulk delete operations
- Deletion history and status tracking

### PnL Summary (`src/pages/pnl_summary.py`)

**Comprehensive profit and loss analysis:**

#### 📊 PnL History Table Tab

- PnL data display with AG Grid
- Event based data refresh from API
- CSV export functionality
- Interactive PnL charts over time
- Formatted columns for dollar amounts and percentages

#### 📈 PnL Analysis by Stock Tab

- **Per-ticker PnL analysis** with dropdown selection
- Net position tracking over time
- Net exposure visualization
- Realized and unrealized PnL breakdown
- Interactive time series charts for individual stocks

## API Integration

### Backend Endpoints

- **Base URL**: `https://fastapi-backend-2.azurewebsites.net`
- **Prices**: `/api/v1/prices`
- **Trades**: `/api/v1/trades`
- **PnL History**: `/api/v1/pnl_history`
- **Upload**: `/api/v1/prices/upload`, `/api/v1/trades/upload`
- **Delete**: `/api/v1/prices/{ticker}`, `/api/v1/trades/{ticker}`

### Data Flow

1. User interactions trigger API calls
2. API client handles HTTP requests/responses
3. Data processing and transformation
4. UI component updates visualizations/tables with new data

## Dependencies

### Core Libraries

- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive charting library
- `requests`: HTTP client for API communication

### UI Components

- `streamlit-aggrid`: Advanced data tables
- `streamlit-plotly-events`: Interactive chart events

## Development Setup

### Prerequisites

- Python 3.10+
- pip package manager

### Installation

```bash
cd frontend
pip install -r requirements.txt
```

### Running the Application

```bash
streamlit run main.py
```

### Development Server

- **URL**: `http://localhost:8501`
- **Auto-reload**: Enabled for development
- **Debug mode**: Available via Streamlit configuration

## Testing

### Test Structure

- Unit tests for API client functionality
- Component integration tests
- Mock API responses for testing

### Running Tests

```bash
cd frontend/tests
python -m pytest
```

## Configuration

### Environment Variables

All configuration is centralized in `src/utils/constants.py`:

- API endpoints and base URLs
- Application styling and colors
- Timeout settings and retry logic

### Streamlit Configuration

- Page title and icon settings
- Layout and theme configuration
- Performance optimization settings

## Deployment

### Docker Support

- Multi-stage build configuration
- Production-optimized container
- Environment variable injection

### Build Process

```bash
docker build -t streamlit-app .
docker run -p 8501:8501 streamlit-app
```

## Non-functional Considerations (Partially Implemented)

### Data Loading

- Lazy loading for large datasets
- Caching for API responses
- Pagination for table displays

### UI Optimization

- Efficient chart rendering
- Debounced user interactions
- Memory management for data processing

## Error Handling

### API Errors

- Network timeout handling
- HTTP status code processing
- User-friendly error messages

### Application Errors

- Graceful degradation
- Fallback UI components
- Error logging and reporting

## Security

### Data Validation

- Input sanitization
- API response validation


### API Security

- HTTPS communication
- Request timeout limits
- Error message sanitization 