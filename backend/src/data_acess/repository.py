from typing import Optional, Sequence, TypeVar, Generic

from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, delete, select, SQLModel

from backend.src.data_acess.db_schema.trade_data import StockPrice, TradeData

T = TypeVar('T', bound=SQLModel)


class TradeDataRepository:
    """Simple repository that accepts engine as constructor argument"""

    def __init__(self, engine: Engine) -> None:
        """
        Initialize repository with database engine

        Args:
            engine: SQLAlchemy engine (can be SQLite, PostgreSQL, etc.)
        """
        self.engine = engine

    def _build_query_with_filters(
        self, 
        model_class: type[T],
        ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> select:
        """Helper method to build queries with optional filters"""
        query = select(model_class)
        if ticker:
            query = query.where(model_class.ticker == ticker)
        if start_date:
            query = query.where(model_class.trade_date >= start_date)
        if end_date:
            query = query.where(model_class.trade_date <= end_date)
        return query

    def get_stock_prices(
        self,
        ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Sequence[StockPrice]:
        """Get stock prices by ticker and/or date range"""
        with Session(self.engine) as session:
            query = self._build_query_with_filters(StockPrice, ticker, start_date, end_date)
            return session.exec(query).all()

    def get_transactions(
        self,
        ticker: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Sequence[TradeData]:
        """Get transactions by ticker and/or date range"""
        with Session(self.engine) as session:
            query = self._build_query_with_filters(TradeData, ticker, start_date, end_date)
            return session.exec(query).all()

    def _add_records(self, records: list[T]) -> int:
        """Helper method to add records to database"""
        with Session(self.engine) as session:
            try:
                session.add_all(records)
                session.commit()
                return len(records)
            except SQLAlchemyError as e:
                session.rollback()
                raise e

    def add_stock_prices(self, stock_prices: list[StockPrice]) -> int:
        """Add multiple stock prices and return the number of records inserted"""
        return self._add_records(stock_prices)

    def add_trades(self, trades: list[TradeData]) -> int:
        """Add multiple trades and return the number of records inserted"""
        return self._add_records(trades)

    def _delete_records_by_ticker(self, model_class: type[T], ticker: str) -> int:
        """Helper method to delete records by ticker"""
        with Session(self.engine) as session:
            result = session.exec(delete(model_class).where(model_class.ticker == ticker))
            session.commit()
            return result.rowcount

    def delete_stock_prices(self, ticker: str) -> int:
        """Delete all stock prices for a given ticker. Returns number of records deleted."""
        return self._delete_records_by_ticker(StockPrice, ticker)

    def delete_trade_data(self, ticker: str) -> int:
        """Delete all trade data for a given ticker. Returns number of records deleted."""
        return self._delete_records_by_ticker(TradeData, ticker)
