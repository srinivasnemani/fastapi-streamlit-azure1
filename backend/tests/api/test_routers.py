from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.src.api import dependencies
from backend.src.api.routers.pnl import router as pnl_router
from backend.src.api.routers.prices import router as prices_router
from backend.src.api.routers.trades import router as trades_router


@pytest.fixture
def mock_repo():
    repo = MagicMock()

    # Create mock objects with proper attribute access
    mock_price = MagicMock()
    mock_price.trade_date = "2023-01-01"
    mock_price.ticker = "AAPL"
    mock_price.close_price = 100
    mock_price.model_dump.return_value = {
        "trade_date": "2023-01-01",
        "ticker": "AAPL",
        "close_price": 100,
    }

    mock_trade = MagicMock()
    mock_trade.trade_date = "2023-01-01"
    mock_trade.ticker = "AAPL"
    mock_trade.quantity = 10
    mock_trade.price = 100
    mock_trade.model_dump.return_value = {
        "trade_date": "2023-01-01",
        "ticker": "AAPL",
        "quantity": 10,
        "price": 100,
    }

    repo.get_stock_prices.return_value = [mock_price]
    repo.get_transactions.return_value = [mock_trade]
    repo.add_stock_prices.return_value = 1
    repo.add_trades.return_value = 1
    repo.delete_stock_prices.return_value = 1
    repo.delete_trade_data.return_value = 1
    return repo


@pytest.fixture
def client(mock_repo):
    app = FastAPI()
    app.include_router(prices_router, prefix="/api/v1")
    app.include_router(trades_router, prefix="/api/v1")
    app.include_router(pnl_router, prefix="/api/v1")
    app.dependency_overrides[dependencies.get_trade_data_repository] = lambda: mock_repo
    return TestClient(app)


def test_get_prices(client):
    response = client.get("/api/v1/prices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["ticker"] == "AAPL"


def test_upload_prices_csv(client, tmp_path):
    csv_content = "date,ticker,close\n2023-01-01,AAPL,100\n"
    file_path = tmp_path / "prices.csv"
    file_path.write_text(csv_content)
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/prices/upload", files={"file": ("prices.csv", f, "text/csv")}
        )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_delete_prices_by_ticker(client):
    response = client.delete("/api/v1/prices/AAPL")
    assert response.status_code == 200
    assert response.json()["deleted"] == 1


def test_get_trades(client):
    response = client.get("/api/v1/trades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["ticker"] == "AAPL"


def test_upload_trades_csv(client, tmp_path):
    csv_content = "date,ticker,quantity,price\n2023-01-01,AAPL,10,100\n"
    file_path = tmp_path / "trades.csv"
    file_path.write_text(csv_content)
    with open(file_path, "rb") as f:
        response = client.post(
            "/api/v1/trades/upload", files={"file": ("trades.csv", f, "text/csv")}
        )
    assert response.status_code == 200
    assert response.json()["inserted"] == 1


def test_delete_trades_by_ticker(client):
    response = client.delete("/api/v1/trades/AAPL")
    assert response.status_code == 200
    assert response.json()["deleted"] == 1


def test_get_pnl_history(client):
    response = client.get("/api/v1/pnl_history")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
