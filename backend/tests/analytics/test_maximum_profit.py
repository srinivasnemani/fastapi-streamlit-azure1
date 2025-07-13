"""
Tests for maximum profit calculation functionality in PnLAnalytics
"""

import pandas as pd
import pytest
from backend.src.analytics.pnl_analytics import PnLAnalytics


class TestMaximumProfit:
    """Test cases for maximum profit calculation"""

    def setup_method(self):
        """Set up test data"""
        # Create sample price data
        self.prices_data = [
            {"trade_date": "2023-01-01", "ticker": "AAPL", "close_price": 150.0},
            {"trade_date": "2023-01-02", "ticker": "AAPL", "close_price": 155.0},
            {"trade_date": "2023-01-03", "ticker": "AAPL", "close_price": 160.0},
            {"trade_date": "2023-01-04", "ticker": "AAPL", "close_price": 145.0},
            {"trade_date": "2023-01-05", "ticker": "AAPL", "close_price": 170.0},
            {"trade_date": "2023-01-01", "ticker": "GOOGL", "close_price": 2500.0},
            {"trade_date": "2023-01-02", "ticker": "GOOGL", "close_price": 2400.0},
            {"trade_date": "2023-01-03", "ticker": "GOOGL", "close_price": 2600.0},
            {"trade_date": "2023-01-04", "ticker": "GOOGL", "close_price": 2300.0},
            {"trade_date": "2023-01-05", "ticker": "GOOGL", "close_price": 2700.0},
        ]
        
        self.prices_df = pd.DataFrame(self.prices_data)
        self.trades_df = pd.DataFrame(columns=["trade_date", "ticker", "quantity", "price"])
        
        self.pnl_analytics = PnLAnalytics(self.trades_df, self.prices_df)

    def test_find_maximum_profit_dates(self):
        """Test finding maximum profit dates for all stocks"""
        result = self.pnl_analytics.find_maximum_profit_dates()
        
        assert "AAPL" in result
        assert "GOOGL" in result
        
        # Check AAPL results
        aapl_result = result["AAPL"]
        assert "long_only" in aapl_result
        assert "short_sale" in aapl_result
        
        # AAPL long only: buy at 145, sell at 170 = 25 profit
        assert aapl_result["long_only"]["max_profit"] == 25.0
        assert str(aapl_result["long_only"]["buy_date"])[:10] == "2023-01-04"
        assert str(aapl_result["long_only"]["sell_date"])[:10] == "2023-01-05"
        
        # AAPL short sale: sell at 160, buy at 145 = 15 profit
        assert aapl_result["short_sale"]["max_profit"] == 15.0
        assert str(aapl_result["short_sale"]["sell_date"])[:10] == "2023-01-03"
        assert str(aapl_result["short_sale"]["buy_date"])[:10] == "2023-01-04"

    def test_calculate_long_only_max_profit(self):
        """Test long only maximum profit calculation"""
        aapl_prices = self.prices_df[self.prices_df["ticker"] == "AAPL"]
        result = self.pnl_analytics._calculate_max_profit_vectorized(aapl_prices, strategy="long_only")
        
        assert result["max_profit"] == 25.0
        assert str(result["buy_date"])[:10] == "2023-01-04"
        assert str(result["sell_date"])[:10] == "2023-01-05"
        assert result["buy_price"] == 145.0
        assert result["sell_price"] == 170.0

    def test_calculate_short_sale_max_profit(self):
        """Test short sale maximum profit calculation"""
        aapl_prices = self.prices_df[self.prices_df["ticker"] == "AAPL"]
        result = self.pnl_analytics._calculate_max_profit_vectorized(aapl_prices, strategy="short_sale")
        
        assert result["max_profit"] == 15.0
        assert str(result["sell_date"])[:10] == "2023-01-03"
        assert str(result["buy_date"])[:10] == "2023-01-04"
        assert result["sell_price"] == 160.0
        assert result["buy_price"] == 145.0

    def test_simple_ascending_prices_long_only(self):
        """Test long only strategy with simple ascending price pattern"""
        ascending_data = [
            {"trade_date": "2023-01-01", "ticker": "ASCEND", "close_price": 100.0},
            {"trade_date": "2023-01-02", "ticker": "ASCEND", "close_price": 110.0},
            {"trade_date": "2023-01-03", "ticker": "ASCEND", "close_price": 120.0},
        ]
        ascending_prices_df = pd.DataFrame(ascending_data)
        ascending_trades_df = pd.DataFrame(columns=["trade_date", "ticker", "quantity", "price"])
        
        pnl_analytics = PnLAnalytics(ascending_trades_df, ascending_prices_df)
        result = pnl_analytics._calculate_max_profit_vectorized(ascending_prices_df, strategy="long_only")
        
        # Should buy at 100 and sell at 120 = 20 profit
        assert result["max_profit"] == 20.0
        assert str(result["buy_date"])[:10] == "2023-01-01"
        assert str(result["sell_date"])[:10] == "2023-01-03"
        assert result["buy_price"] == 100.0
        assert result["sell_price"] == 120.0

    def test_simple_descending_prices_short_sale(self):
        """Test short sale strategy with simple descending price pattern"""
        descending_data = [
            {"trade_date": "2023-01-01", "ticker": "DESCEND", "close_price": 120.0},
            {"trade_date": "2023-01-02", "ticker": "DESCEND", "close_price": 110.0},
            {"trade_date": "2023-01-03", "ticker": "DESCEND", "close_price": 100.0},
        ]
        descending_prices_df = pd.DataFrame(descending_data)
        descending_trades_df = pd.DataFrame(columns=["trade_date", "ticker", "quantity", "price"])
        
        pnl_analytics = PnLAnalytics(descending_trades_df, descending_prices_df)
        result = pnl_analytics._calculate_max_profit_vectorized(descending_prices_df, strategy="short_sale")
        
        # Should sell at 120 and buy at 100 = 20 profit
        assert result["max_profit"] == 20.0
        assert str(result["sell_date"])[:10] == "2023-01-01"
        assert str(result["buy_date"])[:10] == "2023-01-03"
        assert result["sell_price"] == 120.0
        assert result["buy_price"] == 100.0

    def test_get_maximum_profit_summary(self):
        """Test getting maximum profit summary DataFrame"""
        summary_df = self.pnl_analytics.get_maximum_profit_summary()
        
        assert len(summary_df) == 4  # 2 strategies × 2 stocks
        
        # Check columns
        expected_columns = [
            "ticker", "strategy", "buy_date", "sell_date", 
            "max_profit", "buy_price", "sell_price", "profit_percentage"
        ]
        for col in expected_columns:
            assert col in summary_df.columns
        
        # Check AAPL long only entry
        aapl_long = summary_df[
            (summary_df["ticker"] == "AAPL") & 
            (summary_df["strategy"] == "Long Only")
        ].iloc[0]
        
        assert aapl_long["max_profit"] == 25.0
        assert aapl_long["profit_percentage"] == pytest.approx(17.24, rel=0.01)

    def test_single_price_point(self):
        """Test behavior with only one price point per ticker"""
        single_price_data = [
            {"trade_date": "2023-01-01", "ticker": "TSLA", "close_price": 200.0},
        ]
        single_prices_df = pd.DataFrame(single_price_data)
        single_trades_df = pd.DataFrame(columns=["trade_date", "ticker", "quantity", "price"])
        
        pnl_analytics = PnLAnalytics(single_trades_df, single_prices_df)
        result = pnl_analytics.find_maximum_profit_dates()
        
        # Should skip tickers with less than 2 price points
        assert "TSLA" not in result

    def test_declining_prices(self):
        """Test behavior with consistently declining prices"""
        declining_data = [
            {"trade_date": "2023-01-01", "ticker": "DECLINE", "close_price": 100.0},
            {"trade_date": "2023-01-02", "ticker": "DECLINE", "close_price": 90.0},
            {"trade_date": "2023-01-03", "ticker": "DECLINE", "close_price": 80.0},
        ]
        declining_prices_df = pd.DataFrame(declining_data)
        declining_trades_df = pd.DataFrame(columns=["trade_date", "ticker", "quantity", "price"])
        
        pnl_analytics = PnLAnalytics(declining_trades_df, declining_prices_df)
        result = pnl_analytics.find_maximum_profit_dates()
        
        decline_result = result["DECLINE"]
        
        # Long only should have 0 profit (no profit opportunity)
        assert decline_result["long_only"]["max_profit"] == 0.0
        
        # Short sale should have profit (sell at 100, buy at 80 = 20 profit)
        assert decline_result["short_sale"]["max_profit"] == 20.0 