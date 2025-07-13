"""
Pytest tests for FastAPIClient
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
from src.services.api_client import FastAPIClient


@pytest.fixture
def api_client() -> FastAPIClient:
    return FastAPIClient(base_url="http://test.com", timeout=10)


@pytest.fixture
def sample_trades() -> List[Dict[str, Any]]:
    return [
        {"ticker": "AAPL", "trade_date": "2023-01-01", "quantity": 100, "price": 150.0},
        {
            "ticker": "GOOGL",
            "trade_date": "2023-01-01",
            "quantity": 50,
            "price": 2500.0,
        },
    ]


@pytest.fixture
def sample_pnl_data() -> List[Dict[str, Any]]:
    return [
        {
            "ticker": "AAPL",
            "trade_date": "2023-01-01",
            "realized_pnl": 100.0,
            "unrealized_pnl": 50.0,
        },
        {
            "ticker": "GOOGL",
            "trade_date": "2023-01-01",
            "realized_pnl": 200.0,
            "unrealized_pnl": 75.0,
        },
    ]


class TestFastAPIClient:
    def test_init_custom_values(self) -> None:
        client = FastAPIClient(base_url="http://custom.com", timeout=60)
        assert client.base_url == "http://custom.com"
        assert client.timeout == 60

    @patch("requests.get")
    def test_get_trades_success(
        self,
        mock_get: Mock,
        api_client: FastAPIClient,
        sample_trades: List[Dict[str, Any]],
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = sample_trades
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api_client.get_trades()

        assert result is not None
        assert len(result) == 2
        assert result[0]["ticker"] == "AAPL"
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_pnl_history_success(
        self,
        mock_get: Mock,
        api_client: FastAPIClient,
        sample_pnl_data: List[Dict[str, Any]],
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = sample_pnl_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = api_client.get_pnl_history()

        assert result is not None
        assert len(result) == 2
        assert result[0]["realized_pnl"] == 100.0
        mock_get.assert_called_once()

    @patch("requests.post")
    def test_upload_prices_success(
        self, mock_post: Mock, api_client: FastAPIClient
    ) -> None:
        mock_response = Mock()
        mock_response.json.return_value = {"inserted": 5, "status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        mock_file = MagicMock()
        mock_file.name = "test_prices.csv"

        result = api_client.upload_prices(mock_file)

        assert result is not None
        assert result["inserted"] == 5
        mock_post.assert_called_once()

    def test_make_request_success(self, api_client: FastAPIClient) -> None:
        with patch("requests.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            result = api_client._make_request("GET", "/test")

            assert result is not None
            assert result["data"] == "test"

    @pytest.mark.parametrize(
        "method,url,expected_url",
        [
            ("GET", "/test", "http://test.com/test"),
            ("POST", "/api/v1/prices", "http://test.com/api/v1/prices"),
        ],
    )
    def test_make_request_url_construction(
        self, api_client: FastAPIClient, method: str, url: str, expected_url: str
    ) -> None:
        with patch("requests.request") as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status.return_value = None
            mock_request.return_value = mock_response

            api_client._make_request(method, url)

            call_args = mock_request.call_args
            assert call_args[0][1] == expected_url

    def test_upload_prices_with_real_file(
        self, api_client: FastAPIClient, tmp_path: Any
    ) -> None:
        csv_file = tmp_path / "test_prices.csv"
        csv_content = "ticker,trade_date,close_price\nAAPL,2023-01-01,150.0\nGOOGL,2023-01-01,2500.0"
        csv_file.write_text(csv_content)

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = {"inserted": 2, "status": "success"}
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            with open(csv_file, "rb") as f:
                result = api_client.upload_prices(f)

            assert result is not None
            assert result["inserted"] == 2
            mock_post.assert_called_once()
