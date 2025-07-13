import os
import sys
from typing import Set

import pandas as pd
import streamlit as st
from src.components.charts import create_pnl_chart
from src.services.api_client import FastAPIClient
from st_aggrid import AgGrid, GridOptionsBuilder

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        font-size: 1.3rem;
        gap: 2.5rem;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 2rem 0.75rem 2rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def _configure_ag_grid_columns(
    gb: GridOptionsBuilder,
    df: pd.DataFrame,
    dollar_cols: Set[str],
    percent_cols: Set[str],
) -> None:
    """Configure AG Grid columns with proper formatting for dollar and percentage values"""
    column_configs = {
        "dollar": {
            "type": ["numericColumn"],
            "valueFormatter": "x == null ? '' : x.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})",
        },
        "percent": {
            "type": ["numericColumn"],
            "valueFormatter": "x == null ? '' : (x * 100).toFixed(2) + '%' ",
        },
    }
    
    for col in df.columns:
        if col in dollar_cols:
            gb.configure_column(col, **column_configs["dollar"])
        elif col in percent_cols:
            gb.configure_column(col, **column_configs["percent"])


def _load_data_to_session_state(
    api_client: FastAPIClient,
    data_getter: callable,
    session_key: str,
    loading_message: str,
    empty_message: str,
    error_message: str,
) -> None:
    """Load data from API and store in session state with proper error handling"""
    with st.spinner(loading_message):
        data = data_getter()
        if data:
            df = pd.DataFrame(data)
            if not df.empty:
                st.session_state[session_key] = df
            else:
                st.session_state[session_key] = None
                st.warning(empty_message)
        else:
            st.session_state[session_key] = None
            st.error(error_message)


def show() -> None:
    st.header("📊 Data Management")

    api_client = FastAPIClient()

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Stock Prices", "💹 Trade Data", "☁️ Upload Data", "🗑️ Delete Data"]
    )

    with tab1:
        show_stock_prices(api_client)
    with tab2:
        show_trading_data(api_client)
    with tab3:
        show_upload_data(api_client)
    with tab4:
        show_delete_data(api_client)


def show_stock_prices(api_client: FastAPIClient) -> None:
    st.subheader("Stock Prices Data")

    if st.button("🔄 Refresh Stock Prices"):
        _load_data_to_session_state(
            api_client=api_client,
            data_getter=api_client.get_stock_prices,
            session_key="stock_prices_df",
            loading_message="Loading stock prices...",
            empty_message="No stock price data available",
            error_message="Failed to load stock prices data",
        )

    df = st.session_state.get("stock_prices_df", None)
    if df is not None:
        csv = df.to_csv(index=False)
        st.download_button("Download Table as CSV", csv, "stock_prices.csv", "text/csv")

        gb = GridOptionsBuilder.from_dataframe(df)
        if "trade_date" in df.columns:
            gb.configure_column(
                "trade_date",
                type=["dateColumnFilter", "customDateTimeFormat"],
                custom_format_string="yyyy-MM-dd",
            )
        dollar_cols = {
            "long_exposure",
            "short_exposure",
            "long_pnl",
            "short_pnl",
            "total_exposure",
            "net_exposure",
            "total_pnl",
            "cumulative_long_pnl",
            "cumulative_short_pnl",
            "cumulative_total_pnl",
            "close_price",
        }
        percent_cols = {
            "long_pnl_pct",
            "short_pnl_pct",
            "net_pnl_pct",
            "cumulative_long_pnl_pct",
            "cumulative_short_pnl_pct",
            "cumulative_total_pnl_pct",
        }

        _configure_ag_grid_columns(gb, df, dollar_cols, percent_cols)
        gridOptions = gb.build()
        AgGrid(
            df,
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="compact",
        )
    else:
        st.info("Click 'Refresh Stock Prices' to load and download the table.")


def show_trading_data(api_client: FastAPIClient) -> None:
    st.subheader("Trade Data")

    if st.button("🔄 Refresh Trading Data"):
        _load_data_to_session_state(
            api_client=api_client,
            data_getter=api_client.get_trades,
            session_key="trading_data_df",
            loading_message="Loading trading data...",
            empty_message="No trading data available",
            error_message="Failed to load trading data",
        )

    df = st.session_state.get("trading_data_df", None)
    if df is not None:
        csv = df.to_csv(index=False)
        st.download_button("Download Table as CSV", csv, "trading_data.csv", "text/csv")

        gb = GridOptionsBuilder.from_dataframe(df)
        if "date" in df.columns:
            gb.configure_column(
                "date",
                type=["dateColumnFilter", "customDateTimeFormat"],
                custom_format_string="yyyy-MM-dd",
            )
        dollar_cols = {"price", "total_value"}
        _configure_ag_grid_columns(gb, df, dollar_cols, set())
        gridOptions = gb.build()
        AgGrid(
            df,
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="compact",
        )

        col1, col2 = st.columns(2)
        with col1:
            if "quantity" in df.columns and "ticker" in df.columns:
                st.subheader("Latest Net Stocks by Ticker")
                st.bar_chart(df.groupby("ticker")["quantity"].sum())
        with col2:
            if (
                "price" in df.columns
                and "quantity" in df.columns
                and "ticker" in df.columns
            ):
                st.subheader("Latest Total Exposure by Ticker")
                df["total_value"] = df["quantity"] * df["price"]
                st.bar_chart(df.groupby("ticker")["total_value"].sum())
    else:
        st.info("Click 'Refresh Trading Data' to load and download the table.")


def show_upload_data(api_client: FastAPIClient) -> None:
    st.markdown(
        """
        <style>
        .center-upload {
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        section[data-testid="stFileUploader"] > div {
            display: flex !important;
            justify-content: center !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="center-upload">', unsafe_allow_html=True)
        st.subheader("📈 Upload Stock Prices")
        prices_file = st.file_uploader(
            "Choose a CSV file for stock prices", type=["csv"], key="prices_uploader"
        )
        if prices_file is not None:
            if st.button("☁️ Upload Stock Prices"):
                with st.spinner("Uploading stock prices..."):
                    result = api_client.upload_prices(prices_file)
                    if result:
                        st.success(
                            f"✅ Successfully uploaded {result.get('inserted', 0)} stock price records!"
                        )
                    else:
                        st.error("❌ Failed to upload stock prices")
        st.markdown("</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="center-upload">', unsafe_allow_html=True)
        st.subheader("💹 Upload Trading Data")
        trades_file = st.file_uploader(
            "Choose a CSV file for trading data", type=["csv"], key="trades_uploader"
        )
        if trades_file is not None:
            if st.button("☁️ Upload Trading Data"):
                with st.spinner("Uploading trading data..."):
                    result = api_client.upload_trades(trades_file)
                    if result:
                        st.success(
                            f"✅ Successfully uploaded {result.get('inserted', 0)} trading records!"
                        )
                    else:
                        st.error("❌ Failed to upload trading data")
        st.markdown("</div>", unsafe_allow_html=True)


def show_delete_data(api_client: FastAPIClient) -> None:
    st.subheader("🗑️ Delete Data by Ticker")

    prices_data = api_client.get_stock_prices() or []
    trades_data = api_client.get_trades() or []

    prices_df = pd.DataFrame(prices_data)
    prices_tickers = (
        sorted(prices_df["ticker"].dropna().unique())
        if not prices_df.empty and "ticker" in prices_df.columns
        else []
    )

    trades_df = pd.DataFrame(trades_data)
    trades_tickers = (
        sorted(trades_df["ticker"].dropna().unique())
        if not trades_df.empty and "ticker" in trades_df.columns
        else []
    )

    col1, col2 = st.columns(2)
    with col1:
        with st.container():
            st.markdown("###")
            st.markdown("💹 **Delete Stock Prices**")
            st.markdown(
                '<hr style="height:3px;border:none;color:#19b6ff;background-color:#19b6ff;">',
                unsafe_allow_html=True,
            )
            selected_price_ticker = st.selectbox(
                "Select ticker from drop-down delete prices",
                prices_tickers,
                key="delete_price_ticker",
            )
            if st.button("Delete the data", key="delete_price_btn"):
                if selected_price_ticker:
                    with st.spinner(
                        f"Deleting stock prices for {selected_price_ticker}..."
                    ):
                        result = api_client.delete_prices_by_ticker(
                            selected_price_ticker
                        )
                        if result and result.get("deleted", 0) > 0:
                            st.success(
                                f"✅ Deleted {result.get('deleted', 0)} stock price records for {selected_price_ticker}"
                            )
                        else:
                            st.error(
                                f"❌ Failed to delete stock prices for {selected_price_ticker}"
                            )
                else:
                    st.warning("Please select a ticker.")
            st.markdown(
                '<hr style="height:3px;border:none;color:#19b6ff;background-color:#19b6ff;">',
                unsafe_allow_html=True,
            )
    with col2:
        with st.container():
            st.markdown("###")
            st.markdown("📈 **Delete Trading Data**")
            st.markdown(
                '<hr style="height:3px;border:none;color:#19b6ff;background-color:#19b6ff;">',
                unsafe_allow_html=True,
            )
            selected_trade_ticker = st.selectbox(
                "Select ticker from drop-down to delete trades",
                trades_tickers,
                key="delete_trade_ticker",
            )
            if st.button("Delete the data", key="delete_trade_btn"):
                if selected_trade_ticker:
                    with st.spinner(
                        f"Deleting trading data for {selected_trade_ticker}..."
                    ):
                        result = api_client.delete_trades_by_ticker(
                            selected_trade_ticker
                        )
                        if result and result.get("deleted", 0) > 0:
                            st.success(
                                f"✅ Deleted {result.get('deleted', 0)} trading records for {selected_trade_ticker}"
                            )
                        else:
                            st.error(
                                f"❌ Failed to delete trading data for {selected_trade_ticker}"
                            )
                else:
                    st.warning("Please select a ticker.")
            st.markdown(
                '<hr style="height:3px;border:none;color:#19b6ff;background-color:#19b6ff;">',
                unsafe_allow_html=True,
            )


def show_pnl_history(api_client: FastAPIClient) -> None:
    st.subheader("PnL History")

    if st.button("🔄 Refresh PnL Data"):
        _load_data_to_session_state(
            api_client=api_client,
            data_getter=api_client.get_pnl_history,
            session_key="pnl_history_df",
            loading_message="Loading PnL data...",
            empty_message="No PnL data available",
            error_message="Failed to load PnL data",
        )

    df = st.session_state.get("pnl_history_df", None)
    if df is not None:
        csv = df.to_csv(index=False)
        st.download_button("Download Table as CSV", csv, "pnl_history.csv", "text/csv")

        gb = GridOptionsBuilder.from_dataframe(df)
        if "date" in df.columns:
            gb.configure_column(
                "date",
                type=["dateColumnFilter", "customDateTimeFormat"],
                custom_format_string="yyyy-MM-dd",
            )
        dollar_cols = {"pnl", "cumulative_pnl", "daily_pnl"}
        percent_cols = {"pnl_pct", "cumulative_pnl_pct"}
        _configure_ag_grid_columns(gb, df, dollar_cols, percent_cols)
        gridOptions = gb.build()
        AgGrid(
            df,
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="compact",
        )

        create_pnl_chart(df, "date", "pnl", "PnL Over Time")
        if "ticker" in df.columns:
            st.subheader("PnL by Ticker")
            ticker_pnl = df.groupby("ticker")["pnl"].sum().sort_values(ascending=False)
            st.bar_chart(ticker_pnl)
    else:
        st.info("Click 'Refresh PnL Data' to load and download the table.")
