from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

from backend.src.api.config import settings
from backend.src.data_acess.repository import TradeDataRepository


def get_engine() -> Engine:
    engine = create_engine(settings.database_url, echo=False)

    # Create tables if they don't exist
    SQLModel.metadata.create_all(engine)

    return engine


def get_trade_data_repository(
    engine: Engine = Depends(get_engine),
) -> TradeDataRepository:
    return TradeDataRepository(engine)
