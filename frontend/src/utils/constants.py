# API Configuration
API_BASE_URL = "https://fastapi-backend-2.azurewebsites.net"
API_TIMEOUT = 30
PAGE_TITLE = "Stock Trading Dashboard"
PAGE_ICON = "📈"

# API Endpoints (complete URLs)
PRICES_ENDPOINT = "https://fastapi-backend-2.azurewebsites.net/api/v1/prices"
TRADES_ENDPOINT = "https://fastapi-backend-2.azurewebsites.net/api/v1/trades"
PNL_ENDPOINT = "https://fastapi-backend-2.azurewebsites.net/api/v1/pnl_history"

# Upload Endpoints
PRICES_UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/prices/upload"
TRADES_UPLOAD_ENDPOINT = f"{API_BASE_URL}/api/v1/trades/upload"

# Delete Endpoints (base patterns)
PRICES_DELETE_PATTERN = f"{API_BASE_URL}/api/v1/prices"
TRADES_DELETE_PATTERN = f"{API_BASE_URL}/api/v1/trades"

# App Colors (hardcoded values)
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
SUCCESS_COLOR = "#2ca02c"
WARNING_COLOR = "#d62728"
