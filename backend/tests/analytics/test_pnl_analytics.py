import numpy as np
import pandas as pd

from backend.src.analytics.pnl_analytics import PnLAnalytics


def sample_trades_df():
    return pd.DataFrame(
        [
            {
                "trade_date": "2023-01-01",
                "ticker": "AAPL",
                "quantity": 10,
                "price": 100,
            },
            {
                "trade_date": "2023-01-02",
                "ticker": "AAPL",
                "quantity": -5,
                "price": 110,
            },
            {
                "trade_date": "2023-01-01",
                "ticker": "GOOG",
                "quantity": 20,
                "price": 200,
            },
            {"trade_date": "2023-01-03", "ticker": "AAPL", "quantity": 5, "price": 120},
        ]
    )


def sample_prices_df():
    return pd.DataFrame(
        [
            {"trade_date": "2023-01-01", "ticker": "AAPL", "close_price": 105},
            {"trade_date": "2023-01-02", "ticker": "AAPL", "close_price": 115},
            {"trade_date": "2023-01-03", "ticker": "AAPL", "close_price": 125},
            {"trade_date": "2023-01-01", "ticker": "GOOG", "close_price": 210},
            {"trade_date": "2023-01-02", "ticker": "GOOG", "close_price": 215},
            {"trade_date": "2023-01-03", "ticker": "GOOG", "close_price": 220},
        ]
    )


def test_init():
    trades = sample_trades_df()
    prices = sample_prices_df()
    analytics = PnLAnalytics(trades, prices)
    assert isinstance(analytics.trades_df, pd.DataFrame)
    assert isinstance(analytics.prices_df, pd.DataFrame)
    assert set(analytics.trades_df.columns).issuperset(
        {"trade_date", "ticker", "shares", "price"}
    )
    assert set(analytics.prices_df.columns).issuperset(
        {"trade_date", "ticker", "close_price"}
    )


def test_calculate_trade_analytics():
    trades = sample_trades_df()
    prices = sample_prices_df()
    analytics = PnLAnalytics(trades, prices)
    trade_analytics = analytics.calculate_trade_analytics()
    assert isinstance(trade_analytics, pd.DataFrame)
    assert "realized_pnl" in trade_analytics.columns
    assert len(trade_analytics) == len(trades)


def test_create_resampled_prices():
    trades = sample_trades_df()
    prices = sample_prices_df()
    analytics = PnLAnalytics(trades, prices)
    resampled = analytics.create_resampled_prices()
    assert isinstance(resampled, pd.DataFrame)
    assert set(resampled["ticker"]).issuperset({"AAPL", "GOOG"})
    assert set(resampled["trade_date"]).issuperset(
        pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    )


def test_pnl_history():
    trades = sample_trades_df()
    prices = sample_prices_df()
    analytics = PnLAnalytics(trades, prices)
    pnl_history = analytics.pnl_history()
    assert isinstance(pnl_history, pd.DataFrame)
    assert set(["ticker", "trade_date", "close_price", "realized_pnl"]).issubset(
        pnl_history.columns
    )
    # Check that there are no NaN or inf in key columns
    for col in [
        "realized_pnl",
        "position_size_after_trade",
        "position_basis_after_trade",
    ]:
        if col in pnl_history.columns:
            assert not pnl_history[col].isnull().any()
            assert not np.isinf(pnl_history[col]).any()
