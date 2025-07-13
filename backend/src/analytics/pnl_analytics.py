from typing import Any, Dict, List

import numpy as np
import pandas as pd


class PnLAnalytics:
    """
    Portfolio Analytics Library for calculating positions, realized P&L, and unrealized P&L
    Pure analytical functions that work with pandas DataFrames
    """

    def __init__(self, trades_df: pd.DataFrame, prices_df: pd.DataFrame) -> None:
        """
        Initialize the analytics with pandas DataFrames

        Args:
            trades_df: DataFrame with columns ['trade_date', 'ticker', 'quantity', 'price']
            prices_df: DataFrame with columns ['trade_date', 'ticker', 'close_price']
        """
        self.trades_df = trades_df.copy()
        self.trades_df["trade_date"] = pd.to_datetime(self.trades_df["trade_date"])

        self.trades_df = (
            self.trades_df.rename(columns={"quantity": "shares"})
            if "quantity" in self.trades_df.columns
            else self.trades_df
        )
        self.trades_df = self.trades_df.sort_values(["trade_date", "ticker"])

        self.prices_df = prices_df.copy()
        self.prices_df["trade_date"] = pd.to_datetime(self.prices_df["trade_date"])
        self.prices_df = self.prices_df.sort_values(["trade_date", "ticker"])

        self.trade_analytics: pd.DataFrame | None = None

    def calculate_trade_analytics(self) -> pd.DataFrame:
        """
        Calculate trade analytics including realized P&L using the calculate_pnl_for_multiple_tickers function
        """
        self.trade_analytics = self.calculate_pnl_for_multiple_tickers(self.trades_df)
        return self.trade_analytics

    def create_resampled_prices(self) -> pd.DataFrame:
        """
        For each ticker in prices_df, resample dates between min and max dates
        with missing prices filled using nearest data point
        """

        def resample_ticker(
            ticker_name: str, ticker_data: pd.DataFrame
        ) -> pd.DataFrame:
            """Resample a single ticker's price data"""
            ticker_data = ticker_data.set_index("trade_date")
            date_range = pd.date_range(
                start=ticker_data.index.min(), end=ticker_data.index.max(), freq="D"
            )

            resampled = ticker_data.reindex(date_range)
            resampled["close_price"] = resampled["close_price"].ffill().bfill()

            result = resampled.reset_index()
            result["ticker"] = ticker_name
            return result.rename(columns={"index": "trade_date"})

        return pd.concat(
            [
                resample_ticker(ticker, group)
                for ticker, group in self.prices_df.groupby("ticker")
            ],
            ignore_index=True,
        )

    def pnl_history(self) -> pd.DataFrame:
        """
        Create a comprehensive P&L history by merging resampled prices with trade analytics
        and forward filling position data
        """
        if self.trade_analytics is None:
            self.calculate_trade_analytics()

        resampled_prices = self.create_resampled_prices()

        merged_data = resampled_prices.merge(
            self.trade_analytics, on=["trade_date", "ticker"], how="left"
        )

        columns_to_ffill = [
            "position_size_after_trade",
            "position_basis_after_trade",
            "realized_pnl",
        ]
        
        # Only forward fill columns that exist in the merged data
        existing_ffill_columns = [col for col in columns_to_ffill if col in merged_data.columns]
        if existing_ffill_columns:
            merged_data[existing_ffill_columns] = merged_data.groupby("ticker")[
                existing_ffill_columns
            ].ffill()

        # Fill realized_pnl with 0 if it exists
        if "realized_pnl" in merged_data.columns:
            merged_data["realized_pnl"] = merged_data["realized_pnl"].fillna(0)

        # Calculate unrealized P&L only if required columns exist
        if all(col in merged_data.columns for col in ["close_price", "position_basis_after_trade", "position_size_after_trade"]):
            merged_data["unrealized_pnl"] = (
                merged_data["close_price"] - merged_data["position_basis_after_trade"]
            ) * merged_data["position_size_after_trade"]
        else:
            merged_data["unrealized_pnl"] = 0

        # Calculate total P&L
        if "realized_pnl" in merged_data.columns:
            merged_data["total_pnl"] = (
                merged_data["realized_pnl"] + merged_data["unrealized_pnl"]
            )
        else:
            merged_data["total_pnl"] = merged_data["unrealized_pnl"]

        # Vectorized operation to replace the loop
        columns_to_fill = [
            "shares",
            "price",
            "position_size_after_trade",
            "position_basis_after_trade",
            "realized_pnl",
            "unrealized_pnl",
            "total_pnl",
        ]
        
        existing_columns = [col for col in columns_to_fill if col in merged_data.columns]
        if existing_columns:
            merged_data[existing_columns] = merged_data[existing_columns].replace(
                [np.inf, -np.inf], np.nan
            ).fillna(0)

        if "price" in merged_data.columns:
            merged_data = merged_data.rename(columns={"price": "trade_execution_price"})

        return merged_data

    @staticmethod
    def calculate_pnl_for_multiple_tickers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates realized PNL for a series of trades for multiple tickers.
        This version first sorts the data chronologically for each ticker.

        Args:
            df (pd.DataFrame): DataFrame with 'ticker', 'trade_date', 'shares', and 'price' columns.

        Returns:
            pd.DataFrame: A new DataFrame with PNL calculations, sorted by ticker and date.
        """
        df = df.sort_values(["ticker", "trade_date"])

        def process_ticker_trades(group_df: pd.DataFrame) -> pd.DataFrame:
            """Process trades for a single ticker"""
            position_size: int = 0
            position_basis: float = 0.0

            results: Dict[str, List[Any]] = {
                "position_size_after_trade": [],
                "position_basis_after_trade": [],
                "realized_pnl": [],
            }

            for _, trade in group_df.iterrows():
                trade_shares: int = trade["shares"]
                trade_price: float = trade["price"]
                pnl: float = 0.0

                if position_size == 0:
                    # Opening new position
                    position_size = trade_shares
                    position_basis = trade_price

                elif position_size > 0:
                    # Currently long
                    if trade_shares > 0:
                        # Adding to long position
                        total_cost = (position_size * position_basis) + (
                            trade_shares * trade_price
                        )
                        position_size += trade_shares
                        position_basis = total_cost / position_size
                    else:
                        # Selling from long position
                        shares_sold = min(position_size, abs(trade_shares))
                        pnl = (trade_price - position_basis) * shares_sold
                        position_size += trade_shares

                        # Handle position changes
                        if position_size < 0:
                            position_basis = trade_price
                        elif position_size == 0:
                            position_basis = 0.0

                else:  # position_size < 0
                    # Currently short
                    if trade_shares < 0:
                        # Adding to short position
                        total_proceeds = (abs(position_size) * position_basis) + (
                            abs(trade_shares) * trade_price
                        )
                        position_size += trade_shares
                        position_basis = total_proceeds / abs(position_size)
                    else:
                        # Covering short position
                        shares_covered = min(abs(position_size), trade_shares)
                        pnl = (position_basis - trade_price) * shares_covered
                        position_size += trade_shares

                        # Handle position changes
                        if position_size > 0:
                            position_basis = trade_price
                        elif position_size == 0:
                            position_basis = 0.0

                results["position_size_after_trade"].append(position_size)
                results["position_basis_after_trade"].append(position_basis)
                results["realized_pnl"].append(pnl)

            result_df = group_df.copy()
            # Assign the calculated columns to the DataFrame
            for col, values in results.items():
                result_df[col] = values

            return result_df

        return pd.concat(
            [process_ticker_trades(group) for _, group in df.groupby("ticker")],
            ignore_index=True,
        )


    def find_maximum_profit_dates(self) -> Dict[str, Dict[str, Any]]:
        """
        Find the dates when maximum profit can be made for each stock
        with both Long Only and Short Sale constraints.
        
        Returns:
            Dict containing for each ticker:
            - 'long_only': {'buy_date': date, 'sell_date': date, 'max_profit': float}
            - 'short_sale': {'sell_date': date, 'buy_date': date, 'max_profit': float}
        """
        results = {}
        
        for ticker in self.prices_df['ticker'].unique():
            ticker_prices = self.prices_df[self.prices_df['ticker'] == ticker].copy()
            ticker_prices = ticker_prices.sort_values('trade_date')
            
            if len(ticker_prices) < 2:
                continue
                
            # Calculate maximum profit for Long Only strategy
            long_only_result = self._calculate_max_profit_vectorized(ticker_prices, strategy="long_only")
            
            # Calculate maximum profit for Short Sale strategy
            short_sale_result = self._calculate_max_profit_vectorized(ticker_prices, strategy="short_sale")
            
            results[ticker] = {
                'long_only': long_only_result,
                'short_sale': short_sale_result
            }
        
        return results
    
    def _calculate_max_profit_vectorized(self, prices_df: pd.DataFrame, strategy: str) -> Dict[str, Any]:
        """
        Vectorized calculation of maximum profit for both long only and short sale strategies
        
        Args:
            prices_df: DataFrame with 'trade_date' and 'close_price' columns for a single ticker
            strategy: Either 'long_only' or 'short_sale'
            
        Returns:
            Dict with profit details and dates
        """
        if len(prices_df) < 2:
            return self._get_empty_profit_result(strategy)
        
        prices = prices_df['close_price'].values
        dates = prices_df['trade_date'].values
        
        if strategy == "long_only":
            # Long only: buy low, sell high
            # Track minimum price so far and calculate profit as current_price - min_price_so_far
            reference_prices = np.minimum.accumulate(prices)
            profits = prices - reference_prices
            max_profit_idx = profits.argmax()
            max_profit = profits[max_profit_idx]
            
            if max_profit <= 0:
                return self._get_empty_profit_result(strategy)
            
            # Find buy date (minimum price up to sell day)
            buy_idx = (prices[:max_profit_idx+1]).argmin()
            sell_idx = max_profit_idx
            
            return {
                'buy_date': dates[buy_idx],
                'sell_date': dates[sell_idx],
                'max_profit': float(max_profit),
                'buy_price': float(prices[buy_idx]),
                'sell_price': float(prices[sell_idx])
            }
        
        elif strategy == "short_sale":
            # Short sale: sell high, buy low
            # For short sale, we need to find the best sell point (highest price) 
            # and then the best buy point (lowest price) after selling
            max_profit = 0
            best_sell_idx = 0
            best_buy_idx = 0
            
            for sell_idx in range(len(prices) - 1):
                # For each potential sell point, find the best buy point after it
                sell_price = prices[sell_idx]
                min_price_after_sell = np.min(prices[sell_idx + 1:])
                min_price_idx = sell_idx + 1 + np.argmin(prices[sell_idx + 1:])
                
                profit = sell_price - min_price_after_sell
                if profit > max_profit:
                    max_profit = profit
                    best_sell_idx = sell_idx
                    best_buy_idx = min_price_idx
            
            if max_profit <= 0:
                return self._get_empty_profit_result(strategy)
            
            return {
                'sell_date': dates[best_sell_idx],
                'buy_date': dates[best_buy_idx],
                'max_profit': float(max_profit),
                'sell_price': float(prices[best_sell_idx]),
                'buy_price': float(prices[best_buy_idx])
            }
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}. Must be 'long_only' or 'short_sale'")
    
    def _get_empty_profit_result(self, strategy: str) -> Dict[str, Any]:
        """Get empty result structure for when no profit is possible"""
        return {
            'buy_date': None,
            'sell_date': None,
            'max_profit': 0.0,
            'buy_price': None,
            'sell_price': None
        }
    
    def get_maximum_profit_summary(self) -> pd.DataFrame:
        """
        Get a summary DataFrame of maximum profit opportunities for all stocks
        
        Returns:
            DataFrame with columns: ticker, strategy, buy_date, sell_date, max_profit, 
            buy_price, sell_price, profit_percentage
        """
        max_profit_data = self.find_maximum_profit_dates()
        
        summary_data = []
        
        for ticker, strategies in max_profit_data.items():
            # Long Only strategy
            long_only = strategies['long_only']
            if long_only['max_profit'] > 0:
                summary_data.append({
                    'ticker': ticker,
                    'strategy': 'Long Only',
                    'buy_date': long_only['buy_date'],
                    'sell_date': long_only['sell_date'],
                    'max_profit': long_only['max_profit'],
                    'buy_price': long_only['buy_price'],
                    'sell_price': long_only['sell_price'],
                    'profit_percentage': (long_only['max_profit'] / long_only['buy_price'] * 100) if long_only['buy_price'] else 0
                })
            
            # Short Sale strategy
            short_sale = strategies['short_sale']
            if short_sale['max_profit'] > 0:
                summary_data.append({
                    'ticker': ticker,
                    'strategy': 'Short Sale',
                    'buy_date': short_sale['buy_date'],
                    'sell_date': short_sale['sell_date'],
                    'max_profit': short_sale['max_profit'],
                    'buy_price': short_sale['buy_price'],
                    'sell_price': short_sale['sell_price'],
                    'profit_percentage': (short_sale['max_profit'] / short_sale['sell_price'] * 100) if short_sale['sell_price'] else 0
                })
        
        return pd.DataFrame(summary_data)
