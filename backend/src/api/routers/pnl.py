from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from backend.src.analytics.pnl_analytics import PnLAnalytics
from backend.src.api.dependencies import get_trade_data_repository
from backend.src.data_acess.repository import TradeDataRepository

router = APIRouter()


@router.get("/pnl_history")
async def get_pnl_history(
    ticker: Optional[str] = None,
    repo: TradeDataRepository = Depends(get_trade_data_repository),
) -> List[Dict[str, Any]]:
    """
    Get PnL history using PnLAnalytics. Optionally filter by ticker.
    """
    try:
        trades = repo.get_transactions()
        prices = repo.get_stock_prices()
        if not trades or not prices:
            return []
        trades_df = pd.DataFrame([t.model_dump() for t in trades])
        prices_df = pd.DataFrame([p.model_dump() for p in prices])
        pnl_analytics = PnLAnalytics(trades_df, prices_df)
        pnl_history_df = pnl_analytics.pnl_history()
        # Filter by ticker if provided
        if ticker is not None:
            pnl_history_df = pnl_history_df[pnl_history_df["ticker"] == ticker]
        # Replace NaN, inf, and -inf with None for JSON serialization
        result = pnl_history_df.replace([np.inf, -np.inf], None).where(
            pd.notnull(pnl_history_df), None
        )
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching PnL history: {str(e)}"
        )
