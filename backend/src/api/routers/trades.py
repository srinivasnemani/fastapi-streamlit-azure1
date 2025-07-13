from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.src.api.dependencies import get_trade_data_repository
from backend.src.api.utils import ApiUtils
from backend.src.data_acess.db_schema.trade_data import TradeData
from backend.src.data_acess.repository import TradeDataRepository

router = APIRouter()


class TradeResponse(BaseModel):
    date: str
    ticker: str
    quantity: int
    price: float


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> List[Dict[str, Any]]:
    """
    Get trades from the database with optional filtering by ticker and date range.
    """
    try:
        start_date_str = start_date.isoformat() if start_date else None
        end_date_str = end_date.isoformat() if end_date else None

        trade_data = repo.get_transactions(
            ticker=ticker, start_date=start_date_str, end_date=end_date_str
        )

        data_dict = [
            {
                "date": trade.trade_date,
                "ticker": trade.ticker,
                "quantity": trade.quantity,
                "price": trade.price,
            }
            for trade in trade_data
        ]

        return data_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trades: {str(e)}")


@router.post("/trades/upload")
async def upload_trades_csv(
    file: UploadFile = File(...),
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> Dict[str, int]:
    df = pd.read_csv(file.file)
    required_columns = {"date", "ticker", "quantity", "price"}
    field_map = {
        "trade_date": "date",
        "ticker": "ticker",
        "quantity": "quantity",
        "price": "price",
    }
    try:
        trades = ApiUtils.parse_csv_to_models(
            df, TradeData, required_columns, field_map
        )
    except ValueError as e:
        # Though exception handling is managed centrally in middleware layer,
        # this try-except kept to send clear ValueError instructions/message when csv formatting issues is detected.
        raise HTTPException(status_code=400, detail=str(e))
    count = repo.add_trades(trades)
    return {"inserted": count}


@router.delete("/trades/{ticker}")
async def delete_trades_by_ticker(
    ticker: str, repo: TradeDataRepository = Depends(get_trade_data_repository)
) -> Dict[str, int]:
    count = repo.delete_trade_data(ticker)
    return {"deleted": count}
