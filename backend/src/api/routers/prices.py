from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.src.api.dependencies import get_trade_data_repository
from backend.src.api.utils import ApiUtils
from backend.src.data_acess.db_schema.trade_data import StockPrice
from backend.src.data_acess.repository import TradeDataRepository

router = APIRouter()


class PriceResponse(BaseModel):
    date: str
    ticker: str
    close: float


@router.get("/prices", response_model=List[PriceResponse])
async def get_prices(
    ticker: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> List[Dict[str, Any]]:
    stock_price_data = repo.get_stock_prices(
        ticker=ticker, start_date=start_date, end_date=end_date
    )
    data_dict = [
        {"date": price.trade_date, "ticker": price.ticker, "close": price.close_price}
        for price in stock_price_data
    ]
    return data_dict


@router.post("/prices/upload")
async def upload_prices_csv(
    file: UploadFile = File(...),
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> Dict[str, int]:
    df = pd.read_csv(file.file)
    required_columns = {"date", "ticker", "close"}
    field_map = {"trade_date": "date", "ticker": "ticker", "close_price": "close"}
    try:
        stock_prices = ApiUtils.parse_csv_to_models(
            df, StockPrice, required_columns, field_map
        )
    except ValueError as e:
        # Though exception handling is managed centrally in middleware layer,
        # this try-except kept to send clear ValueError instructions/message when csv formatting issues is detected.
        raise HTTPException(status_code=400, detail=str(e))
    count = repo.add_stock_prices(stock_prices)
    return {"inserted": count}


@router.delete("/prices/{ticker}")
async def delete_prices_by_ticker(
    ticker: str, repo: TradeDataRepository = Depends(get_trade_data_repository)
) -> Dict[str, int]:
    count = repo.delete_stock_prices(ticker)
    return {"deleted": count}
