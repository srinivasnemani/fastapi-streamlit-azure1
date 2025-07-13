from typing import Optional, Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        font-size: 1.5rem !important;
        gap: 3rem;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1.2rem 2.5rem 1.2rem 2.5rem !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab"] > div {
        font-weight: bold !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def _create_chart_figure(
    chart_type: str, data: pd.DataFrame, x_col: str, y_col: str, title: str, color_col: Optional[str] = None
) -> Any:
    """Factory function to create chart figures"""
    chart_creators = {
        "line": px.line,
        "bar": px.bar,
    }
    
    creator = chart_creators[chart_type]
    kwargs = {"x": x_col, "y": y_col, "title": title}
    if color_col:
        kwargs["color"] = color_col
    
    return creator(data, **kwargs)


def create_line_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None,
) -> None:
    """Create a line chart using Plotly"""
    try:
        fig = _create_chart_figure("line", data, x_col, y_col, title, color_col)

        fig.update_layout(
            xaxis_title=x_col.replace("_", " ").title(),
            yaxis_title=y_col.replace("_", " ").title(),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating line chart: {str(e)}")


def create_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color_col: Optional[str] = None,
) -> None:
    """Create a bar chart using Plotly"""
    try:
        fig = _create_chart_figure("bar", data, x_col, y_col, title, color_col)

        fig.update_layout(
            xaxis_title=x_col.replace("_", " ").title(),
            yaxis_title=y_col.replace("_", " ").title(),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating bar chart: {str(e)}")


def create_pnl_chart(data: pd.DataFrame, x_col: str, y_col: str, title: str) -> None:
    """Create a PnL chart with positive/negative coloring"""
    try:
        fig = go.Figure()

        colors = np.where(data[y_col] >= 0, "green", "red")

        fig.add_trace(
            go.Bar(x=data[x_col], y=data[y_col], marker_color=colors, name="PnL")
        )

        fig.update_layout(
            title=title,
            xaxis_title=x_col.replace("_", " ").title(),
            yaxis_title=y_col.replace("_", " ").title(),
            height=400,
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating PnL chart: {str(e)}")


def display_data_table(data: pd.DataFrame, title: str) -> None:
    """Display data in a formatted table"""
    try:
        st.subheader(title)
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying table: {str(e)}")
