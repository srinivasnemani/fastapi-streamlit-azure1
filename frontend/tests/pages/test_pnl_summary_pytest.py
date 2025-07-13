"""
Pytest integration tests for PnL summary page (reduced)
"""

import os
import sys
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# Add the frontend directory to sys.path for imports
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    if frontend_dir not in sys.path:
        sys.path.insert(0, frontend_dir)
    from src.pages import pnl_summary
    from src.services.api_client import FastAPIClient
except ImportError:
    # Fallback for when running tests directly
    pass


@pytest.fixture
def sample_prices_data():
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "GOOGL"],
            "trade_date": ["2023-01-01", "2023-01-01"],
            "close_price": [150.0, 2500.0],
        }
    )


@pytest.fixture
def sample_trades_data():
    return pd.DataFrame(
        {
            "ticker": ["AAPL", "GOOGL"],
            "trade_date": ["2023-01-01", "2023-01-01"],
            "quantity": [100, 50],
            "price": [145.0, 2450.0],
        }
    )


@pytest.fixture
def mock_api_client():
    return Mock(spec=FastAPIClient)


class TestPnLSummary:
    @patch("streamlit.subheader")
    @patch("streamlit.button")
    @patch("streamlit.spinner")
    def test_show_pnl_history_structure(
        self, mock_spinner, mock_button, mock_subheader, mock_api_client
    ):
        mock_button.return_value = False
        pnl_summary.show_pnl_history(mock_api_client)
        mock_subheader.assert_called_once_with("PnL History")
        mock_button.assert_called_once_with("🔄 Refresh PnL Data")

    @patch("streamlit.subheader")
    @patch("streamlit.selectbox")
    def test_show_pnl_analysis_per_stock_structure(
        self, mock_selectbox, mock_subheader, mock_api_client
    ):
        mock_selectbox.return_value = "AAPL"
        with patch("streamlit.session_state") as mock_session:
            mock_session.get.return_value = pd.DataFrame()
            pnl_summary.show_pnl_analysis_per_stock(mock_api_client)
            mock_subheader.assert_called_once_with("Per-Ticker Analysis")

    @patch("streamlit.subheader")
    @patch("streamlit.selectbox")
    def test_show_pnl_analysis_no_data(
        self, mock_selectbox, mock_subheader, mock_api_client
    ):
        with patch("streamlit.session_state") as mock_session:
            mock_session.get.return_value = None
            with patch("streamlit.info") as mock_info:
                pnl_summary.show_pnl_analysis_per_stock(mock_api_client)
                mock_info.assert_called_once()

    def test_perform_pnl_analysis_success(self, sample_prices_data, sample_trades_data):
        result = pnl_summary.perform_pnl_analysis(
            sample_prices_data, sample_trades_data
        )
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "pnl" in result.columns
        assert "cumulative_pnl" in result.columns

    def test_perform_pnl_analysis_exception(self):
        with patch("streamlit.error") as mock_error:
            result = pnl_summary.perform_pnl_analysis(None, None)
            assert isinstance(result, pd.DataFrame)
            assert result.empty
            mock_error.assert_called_once()

    def test_perform_pnl_analysis_empty_data(self):
        empty_prices = pd.DataFrame()
        empty_trades = pd.DataFrame()
        result = pnl_summary.perform_pnl_analysis(empty_prices, empty_trades)
        assert isinstance(result, pd.DataFrame)

    def test_pnl_analysis_calculation_accuracy(
        self, sample_prices_data, sample_trades_data
    ):
        result = pnl_summary.perform_pnl_analysis(
            sample_prices_data, sample_trades_data
        )
        if not result.empty:
            assert pd.api.types.is_numeric_dtype(result["pnl"])
            assert pd.api.types.is_numeric_dtype(result["cumulative_pnl"])
            cumulative_pnl = result["cumulative_pnl"].dropna()
            if len(cumulative_pnl) > 1:
                diffs = cumulative_pnl.diff().dropna()
                assert (diffs >= 0).all() or (diffs <= 0).all()
