"""
Pytest tests for constants module (reduced)
"""

import os
import sys

import pytest

# Add the frontend directory to sys.path for imports
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
    if frontend_dir not in sys.path:
        sys.path.insert(0, frontend_dir)
    from src.utils.constants import (
        API_BASE_URL,
        API_TIMEOUT,
        PAGE_ICON,
        PAGE_TITLE,
        PNL_ENDPOINT,
        PRICES_ENDPOINT,
        PRIMARY_COLOR,
        SECONDARY_COLOR,
        SUCCESS_COLOR,
        TRADES_ENDPOINT,
        WARNING_COLOR,
    )
except ImportError:
    # Fallback for when running tests directly
    pass


@pytest.fixture
def all_constants():
    return {
        "API_BASE_URL": API_BASE_URL,
        "API_TIMEOUT": API_TIMEOUT,
        "PAGE_TITLE": PAGE_TITLE,
        "PAGE_ICON": PAGE_ICON,
        "PRICES_ENDPOINT": PRICES_ENDPOINT,
        "TRADES_ENDPOINT": TRADES_ENDPOINT,
        "PNL_ENDPOINT": PNL_ENDPOINT,
        "PRIMARY_COLOR": PRIMARY_COLOR,
        "SECONDARY_COLOR": SECONDARY_COLOR,
        "SUCCESS_COLOR": SUCCESS_COLOR,
        "WARNING_COLOR": WARNING_COLOR,
    }


class TestConstants:
    def test_api_configuration_constants(self, all_constants):
        assert isinstance(all_constants["API_BASE_URL"], str)
        assert isinstance(all_constants["API_TIMEOUT"], int)
        assert all_constants["API_BASE_URL"].startswith("http")
        assert all_constants["API_TIMEOUT"] > 0

    def test_app_configuration_constants(self, all_constants):
        assert isinstance(all_constants["PAGE_TITLE"], str)
        assert isinstance(all_constants["PAGE_ICON"], str)
        assert len(all_constants["PAGE_TITLE"]) > 0
        assert len(all_constants["PAGE_ICON"]) > 0

    def test_api_endpoints_constants(self, all_constants):
        endpoints = [
            all_constants["PRICES_ENDPOINT"],
            all_constants["TRADES_ENDPOINT"],
            all_constants["PNL_ENDPOINT"],
        ]
        for endpoint in endpoints:
            assert isinstance(endpoint, str)
            assert endpoint.startswith(all_constants["API_BASE_URL"])
        assert "/api/v1/prices" in all_constants["PRICES_ENDPOINT"]
        assert "/api/v1/trades" in all_constants["TRADES_ENDPOINT"]
        assert "/api/v1/pnl_history" in all_constants["PNL_ENDPOINT"]

    def test_color_constants(self, all_constants):
        colors = [
            all_constants["PRIMARY_COLOR"],
            all_constants["SECONDARY_COLOR"],
            all_constants["SUCCESS_COLOR"],
            all_constants["WARNING_COLOR"],
        ]
        for color in colors:
            assert isinstance(color, str)
            assert color.startswith("#")
            assert len(color) == 7
            assert all(c in "0123456789abcdefABCDEF" for c in color[1:])

    def test_endpoint_urls_are_valid(self, all_constants):
        endpoints = [
            all_constants["PRICES_ENDPOINT"],
            all_constants["TRADES_ENDPOINT"],
            all_constants["PNL_ENDPOINT"],
        ]
        for endpoint in endpoints:
            assert endpoint.startswith("http")
            assert "://" in endpoint
            assert "/api/v1/" in endpoint

    def test_timeout_value_is_reasonable(self, all_constants):
        assert all_constants["API_TIMEOUT"] > 0
        assert all_constants["API_TIMEOUT"] < 300

    def test_base_url_format(self, all_constants):
        assert all_constants["API_BASE_URL"].startswith("http")
        assert "://" in all_constants["API_BASE_URL"]
        assert not all_constants["API_BASE_URL"].endswith("/")

    def test_all_constants_are_defined(self):
        expected_constants = [
            "API_BASE_URL",
            "API_TIMEOUT",
            "PAGE_TITLE",
            "PAGE_ICON",
            "PRICES_ENDPOINT",
            "TRADES_ENDPOINT",
            "PNL_ENDPOINT",
            "PRIMARY_COLOR",
            "SECONDARY_COLOR",
            "SUCCESS_COLOR",
            "WARNING_COLOR",
        ]
        for constant_name in expected_constants:
            assert hasattr(sys.modules["src.utils.constants"], constant_name)

    def test_constants_are_not_none(self):
        constants = [
            API_BASE_URL,
            API_TIMEOUT,
            PAGE_TITLE,
            PAGE_ICON,
            PRICES_ENDPOINT,
            TRADES_ENDPOINT,
            PNL_ENDPOINT,
            PRIMARY_COLOR,
            SECONDARY_COLOR,
            SUCCESS_COLOR,
            WARNING_COLOR,
        ]
        for constant in constants:
            assert constant is not None
