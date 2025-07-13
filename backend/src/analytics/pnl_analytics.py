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
