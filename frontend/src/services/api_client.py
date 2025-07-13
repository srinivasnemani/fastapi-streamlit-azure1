from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from src.utils.constants import (
    API_BASE_URL,
    API_TIMEOUT,
    PRICES_ENDPOINT,
    TRADES_ENDPOINT,
    PNL_ENDPOINT,
    PRICES_UPLOAD_ENDPOINT,
    TRADES_UPLOAD_ENDPOINT,
    PRICES_DELETE_PATTERN,
    TRADES_DELETE_PATTERN,
    MAX_PROFIT_ENDPOINT,
)


class FastAPIClient:
    def __init__(
        self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Make HTTP request to the API"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None

    def get_stock_prices(self) -> Optional[List[Dict[str, Any]]]:
        """Get stock prices from the API"""
        try:
            response = requests.get(PRICES_ENDPOINT, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None

    def get_trades(self) -> Optional[List[Dict[str, Any]]]:
        """Get trading data from the API"""
        try:
            response = requests.get(TRADES_ENDPOINT, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None

    def get_pnl_history(self) -> Optional[List[Dict[str, Any]]]:
        """Get PnL history from the API"""
        try:
            response = requests.get(PNL_ENDPOINT, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None

    def get_max_profit(self) -> Optional[list[dict]]:
        """Get max profit summary data from the API"""
        try:
            response = requests.get(MAX_PROFIT_ENDPOINT, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None

    def upload_prices(self, file: Any) -> Optional[Dict[str, Any]]:
        """Upload stock prices CSV file"""
        try:
            files = {"file": file}
            response = requests.post(
                PRICES_UPLOAD_ENDPOINT,
                files=files,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Upload failed: {str(e)}")
            return None

    def upload_trades(self, file: Any) -> Optional[Dict[str, Any]]:
        """Upload trading data CSV file"""
        try:
            files = {"file": file}
            response = requests.post(
                TRADES_UPLOAD_ENDPOINT,
                files=files,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Upload failed: {str(e)}")
            return None

    def delete_prices_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Delete stock prices by ticker"""
        try:
            response = requests.delete(
                f"{PRICES_DELETE_PATTERN}/{ticker}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Delete failed: {str(e)}")
            return None

    def delete_trades_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Delete trading data by ticker"""
        try:
            response = requests.delete(
                f"{TRADES_DELETE_PATTERN}/{ticker}",
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Delete failed: {str(e)}")
            return None
