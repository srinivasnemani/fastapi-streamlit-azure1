from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend.src.analytics.pnl_analytics import PnLAnalytics
from backend.src.api.dependencies import get_trade_data_repository
from backend.src.data_acess.repository import TradeDataRepository

router = APIRouter()


@router.get("/max_profit")
async def get_maximum_profit_data(
    ticker: Optional[str] = None,
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> List[Dict[str, Any]]:
    """
    Get maximum profit summary data for all stocks with both Long Only and Short Sale strategies.
    Returns JSON data with ticker, strategy, buy_date, sell_date, max_profit, buy_price, sell_price, and profit_percentage.
    Optionally filter by ticker.
    """
    try:
        trades = repo.get_transactions()
        prices = repo.get_stock_prices()
        if not prices:
            return []
        
        prices_df = pd.DataFrame([p.model_dump() for p in prices])
        trades_df = pd.DataFrame([t.model_dump() for t in trades]) if trades else pd.DataFrame()
        
        pnl_analytics = PnLAnalytics(trades_df, prices_df)
        summary_df = pnl_analytics.get_maximum_profit_summary()
        
        # Filter by ticker if provided
        if ticker is not None:
            summary_df = summary_df[summary_df["ticker"] == ticker]
        
        # Convert DataFrame to list of dictionaries for JSON response
        result = summary_df.replace([np.inf, -np.inf], None).where(
            pd.notnull(summary_df), None
        ).to_dict(orient="records")
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error calculating maximum profit data: {str(e)}"
        ) 