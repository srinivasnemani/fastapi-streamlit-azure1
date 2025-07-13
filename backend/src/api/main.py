from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.exception_handling import ExceptionMiddleware
from .middleware.logging import LoggingMiddleware
from .routers import pnl, prices, trades

# Configuration for CORS middleware
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": False,  # Must be False when using allow_origins=["*"]
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
}

# Router configuration
ROUTERS = [
    (prices.router, "prices"),
    (trades.router, "trades"),
    (pnl.router, "pnl"),
]

app = FastAPI(
    title="Portfolio Analytics API",
    description="API for portfolio analytics and trading data",
    version="1.0.0",
)

# Add middleware
app.add_middleware(CORSMiddleware, **CORS_CONFIG)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ExceptionMiddleware)

# Include routers
for router, tag in ROUTERS:
    app.include_router(router, prefix="/api/v1", tags=[tag])


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Portfolio Analytics API"}


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy"}
