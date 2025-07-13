from sqlmodel import Field, SQLModel


class StockPrice(SQLModel, table=True):
    __tablename__ = "stock_prices"
    trade_date: str = Field(primary_key=True, index=True)
    ticker: str = Field(primary_key=True, index=True, max_length=10)
    close_price: float


class TradeData(SQLModel, table=True):
    __tablename__ = "trade_data"
    trade_date: str = Field(primary_key=True, index=True)
    ticker: str = Field(primary_key=True, index=True, max_length=10)
    quantity: int = Field(primary_key=True)
    price: float = Field(primary_key=True)
