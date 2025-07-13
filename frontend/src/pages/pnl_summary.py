from typing import Set

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.components.charts import create_pnl_chart
from src.services.api_client import FastAPIClient
from st_aggrid import AgGrid, GridOptionsBuilder


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


def _configure_ag_grid_columns(
    gb, df: pd.DataFrame, dollar_cols: Set[str], percent_cols: Set[str]
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


def show() -> None:
    st.header("💹 PnL Summary")

    api_client = FastAPIClient()

    tab1, tab2, tab3 = st.tabs(["📊 PnL History Table", "📈 PnL Analysis by stock", "🏆 Max Profit Analysis Dates"])

    with tab1:
        show_pnl_history(api_client)

    with tab2:
        show_pnl_analysis_per_stock(api_client)

    with tab3:
        show_max_profit_table(api_client)


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

        if not df.empty and "pnl" in df.columns:
            create_pnl_chart(df, "date", "pnl", "PnL Over Time")
    else:
        st.info("Click 'Refresh PnL Data' to load and download the table.")


def show_pnl_analysis_per_stock(api_client: FastAPIClient) -> None:
    """Show per-stock PnL and exposure analysis"""
    st.subheader("Per-Ticker Analysis")

    if st.button("🔄 Refresh PnL Analysis Data", key="refresh_pnl_analysis"):
        _load_data_to_session_state(
            api_client=api_client,
            data_getter=api_client.get_pnl_history,
            session_key="pnl_analysis_df",
            loading_message="Loading PnL analysis data...",
            empty_message="No PnL data available",
            error_message="Failed to load PnL data",
        )

    df = st.session_state.get("pnl_analysis_df", None)
    if df is None or df.empty or "ticker" not in df.columns:
        st.info(
            "No PnL analysis data available. Please click 'Refresh PnL Analysis Data' to load the data."
        )
        return

    tickers = sorted(df["ticker"].dropna().unique())
    selected_ticker = st.selectbox(
        "Select a ticker for analysis from drop-down",
        tickers,
        key="pnl_analysis_ticker",
    )

    if "trade_date" not in df.columns:
        st.warning("No 'trade_date' column found in data. Cannot plot time series.")
        return

    ticker_df = df[df["ticker"] == selected_ticker].sort_values("trade_date")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Net Position Over Time: {selected_ticker}**")
        if "position_size_after_trade" in ticker_df.columns:
            fig_pos = go.Figure()
            fig_pos.add_trace(
                go.Scatter(
                    x=ticker_df["trade_date"],
                    y=ticker_df["position_size_after_trade"],
                    name="Net Position",
                    line=dict(color="#1f77b4"),
                )
            )
            fig_pos.update_layout(
                yaxis_title="Net Position",
                xaxis_title="Date",
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig_pos, use_container_width=True)
        else:
            st.info("'position_size_after_trade' data not available for this ticker.")
    with col2:
        st.markdown(f"**Net Exposure Over Time: {selected_ticker}**")
        if (
            "position_size_after_trade" in ticker_df.columns
            and "position_basis_after_trade" in ticker_df.columns
        ):
            net_exposure = (
                ticker_df["position_size_after_trade"]
                * ticker_df["position_basis_after_trade"]
            )
            fig_exp = go.Figure()
            fig_exp.add_trace(
                go.Scatter(
                    x=ticker_df["trade_date"],
                    y=net_exposure,
                    name="Net Exposure ($)",
                    line=dict(color="#19b6ff"),
                )
            )
            fig_exp.update_layout(
                yaxis_title="Net Exposure ($)",
                xaxis_title="Date",
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig_exp, use_container_width=True)
        else:
            st.info(
                "'position_size_after_trade' or 'position_basis_after_trade' data not available for this ticker."
            )

    st.markdown(f"**P&L Over Time: {selected_ticker}**")
    fig2 = go.Figure()
    has_any = False
    if "realized_pnl" in ticker_df.columns:
        fig2.add_trace(
            go.Scatter(
                x=ticker_df["trade_date"],
                y=ticker_df["realized_pnl"],
                name="Realized P&L",
                line=dict(color="#2ca02c"),
            )
        )
        has_any = True
    if "unrealized_pnl" in ticker_df.columns:
        fig2.add_trace(
            go.Scatter(
                x=ticker_df["trade_date"],
                y=ticker_df["unrealized_pnl"],
                name="Unrealized P&L",
                line=dict(color="#ff7f0e"),
            )
        )
        has_any = True
    if "total_mtm" in ticker_df.columns:
        fig2.add_trace(
            go.Scatter(
                x=ticker_df["trade_date"],
                y=ticker_df["total_mtm"],
                name="Total MtM",
                line=dict(color="#d62728"),
            )
        )
        has_any = True
    if "total_pnl" in ticker_df.columns:
        fig2.add_trace(
            go.Scatter(
                x=ticker_df["trade_date"],
                y=ticker_df["total_pnl"],
                name="Total P&L",
                line=dict(color="#9467bd"),
            )
        )
        has_any = True

    if has_any:
        fig2.update_layout(
            yaxis_title="P&L ($)",
            xaxis_title="Date",
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No P&L data available for this ticker.")


def show_max_profit_table(api_client: FastAPIClient) -> None:
    st.subheader("Max Profit Summary Table")

    if st.button("🔄 Refresh Max Profit Data", key="refresh_max_profit"):
        _load_data_to_session_state(
            api_client=api_client,
            data_getter=api_client.get_max_profit,
            session_key="max_profit_df",
            loading_message="Loading max profit data...",
            empty_message="No max profit data available",
            error_message="Failed to load max profit data",
        )

    df = st.session_state.get("max_profit_df", None)
    if df is not None:
        # Format columns as requested
        def safe_format(val):
            try:
                return f"{float(val):.2f}"
            except (ValueError, TypeError):
                return val
        for col in ["max_profit", "buy_price", "sell_price", "profit_percentage"]:
            if col in df.columns:
                df[col] = df[col].apply(safe_format)
        # Format date columns
        for col in ["buy_date", "sell_date"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x)[:10] if pd.notnull(x) and len(str(x)) >= 10 else x)

        csv = df.to_csv(index=False)
        st.download_button("Download Table as CSV", csv, "max_profit.csv", "text/csv")

        gb = GridOptionsBuilder.from_dataframe(df)
        dollar_cols = set()  # All formatting is handled above
        percent_cols = set()
        _configure_ag_grid_columns(gb, df, dollar_cols, percent_cols)
        gridOptions = gb.build()
        AgGrid(
            df,
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="compact",
        )
    else:
        st.info("Click 'Refresh Max Profit Data' to load and download the table.")


def perform_pnl_analysis(
    prices_df: pd.DataFrame, trades_df: pd.DataFrame
) -> pd.DataFrame:
    """Perform PnL analysis on the data"""
    try:
        merged_df = pd.merge(
            trades_df, prices_df, on=["ticker", "trade_date"], how="left"
        )

        merged_df["pnl"] = (
            merged_df["close_price"] - merged_df["price"]
        ) * merged_df["quantity"]

        daily_pnl = merged_df.groupby("trade_date")["pnl"].sum().reset_index()
        daily_pnl["cumulative_pnl"] = daily_pnl["pnl"].cumsum()
        daily_pnl["daily_pnl"] = daily_pnl["pnl"]

        return daily_pnl
    except Exception as e:
        st.error(f"Error in PnL analysis: {str(e)}")
        return pd.DataFrame()
