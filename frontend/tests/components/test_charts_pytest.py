"""
Pytest tests for charts components
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
from src.components.charts import create_bar_chart, create_line_chart, create_pnl_chart


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "value": [100, 150, 200],
            "category": ["A", "B", "A"],
        }
    )


@pytest.fixture
def pnl_data_mixed() -> pd.DataFrame:
    return pd.DataFrame(
        {"date": ["2023-01-01", "2023-01-02", "2023-01-03"], "pnl": [100, -50, 200]}
    )


class TestCharts:
    @patch("streamlit.plotly_chart")
    @patch("plotly.express.line")
    def test_create_line_chart_success(
        self, mock_px_line: Mock, mock_st_plotly: Mock, sample_data: pd.DataFrame
    ) -> None:
        mock_fig = Mock()
        mock_px_line.return_value = mock_fig
        create_line_chart(sample_data, "date", "value", "Test Chart")
        mock_px_line.assert_called_once_with(
            sample_data, x="date", y="value", title="Test Chart"
        )
        mock_fig.update_layout.assert_called_once()
        mock_st_plotly.assert_called_once()

    @patch("streamlit.plotly_chart")
    @patch("plotly.express.bar")
    def test_create_bar_chart_success(
        self, mock_px_bar: Mock, mock_st_plotly: Mock, sample_data: pd.DataFrame
    ) -> None:
        mock_fig = Mock()
        mock_px_bar.return_value = mock_fig
        create_bar_chart(sample_data, "date", "value", "Test Bar Chart")
        mock_px_bar.assert_called_once_with(
            sample_data, x="date", y="value", title="Test Bar Chart"
        )
        mock_fig.update_layout.assert_called_once()
        mock_st_plotly.assert_called_once()

    @patch("streamlit.plotly_chart")
    @patch("plotly.graph_objects.Figure")
    def test_create_pnl_chart_success(
        self, mock_go_figure: Mock, mock_st_plotly: Mock, pnl_data_mixed: pd.DataFrame
    ) -> None:
        mock_fig = Mock()
        mock_go_figure.return_value = mock_fig
        create_pnl_chart(pnl_data_mixed, "date", "pnl", "Test PnL Chart")
        mock_go_figure.assert_called_once()
        mock_fig.add_trace.assert_called_once()
        mock_fig.update_layout.assert_called_once()
        mock_st_plotly.assert_called_once()

    def test_create_pnl_chart_color_logic(self) -> None:
        pnl_data = pd.DataFrame(
            {"date": ["2023-01-01", "2023-01-02"], "pnl": [100, -50]}
        )
        expected_colors = np.array(["green", "red"])
        colors = np.where(pnl_data["pnl"] >= 0, "green", "red")
        np.testing.assert_array_equal(colors, expected_colors)

    @patch("streamlit.plotly_chart")
    @patch("plotly.express.line")
    def test_create_line_chart_with_color(
        self, mock_px_line: Mock, mock_st_plotly: Mock, sample_data: pd.DataFrame
    ) -> None:
        mock_fig = Mock()
        mock_px_line.return_value = mock_fig
        create_line_chart(sample_data, "date", "value", "Test Chart", "category")
        mock_px_line.assert_called_once_with(
            sample_data, x="date", y="value", color="category", title="Test Chart"
        )

    def test_chart_functions_return_none(self, sample_data: pd.DataFrame) -> None:
        with patch("streamlit.plotly_chart"):
            with patch("plotly.express.line"):
                result = create_line_chart(sample_data, "date", "value", "Test Chart")
                assert result is None
        with patch("streamlit.plotly_chart"):
            with patch("plotly.express.bar"):
                result = create_bar_chart(
                    sample_data, "date", "value", "Test Bar Chart"
                )
                assert result is None
        with patch("streamlit.plotly_chart"):
            with patch("plotly.graph_objects.Figure"):
                result = create_pnl_chart(
                    sample_data, "date", "value", "Test PnL Chart"
                )
                assert result is None
