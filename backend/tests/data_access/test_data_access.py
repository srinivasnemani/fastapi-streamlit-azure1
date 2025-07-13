from unittest.mock import MagicMock, patch

from backend.src.data_acess.db_schema.trade_data import StockPrice, TradeData
from backend.src.data_acess.repository import TradeDataRepository


@patch("backend.src.data_acess.repository.Session")
def test_get_stock_prices(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    # Mock the query chain
    mock_query = MagicMock()
    mock_session.exec.return_value = mock_query
    mock_query.all.return_value = [
        StockPrice(trade_date="2025-06-10", ticker="AAPL", close_price=150)
    ]

    # Test get_stock_prices
    result = repo.get_stock_prices(ticker="AAPL")
    assert len(result) == 1
    assert result[0].ticker == "AAPL"
    assert result[0].close_price == 150


@patch("backend.src.data_acess.repository.Session")
def test_get_transactions(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    # Mock the query chain
    mock_query = MagicMock()
    mock_session.exec.return_value = mock_query
    mock_query.all.return_value = [
        TradeData(trade_date="2025-06-10", ticker="AAPL", quantity=10, price=150)
    ]

    # Test get_transactions
    result = repo.get_transactions(ticker="AAPL")
    assert len(result) == 1
    assert result[0].ticker == "AAPL"
    assert result[0].quantity == 10


@patch("backend.src.data_acess.repository.Session")
def test_add_stock_prices(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    stock_prices = [
        StockPrice(trade_date="2025-06-10", ticker="AAPL", close_price=150),
        StockPrice(trade_date="2025-06-11", ticker="AAPL", close_price=155),
    ]

    # Test add_stock_prices
    result = repo.add_stock_prices(stock_prices)
    assert result == 2
    mock_session.add_all.assert_called_once_with(stock_prices)
    mock_session.commit.assert_called_once()


@patch("backend.src.data_acess.repository.Session")
def test_add_trades(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    trades = [
        TradeData(trade_date="2025-06-10", ticker="AAPL", quantity=10, price=150),
        TradeData(trade_date="2025-06-11", ticker="AAPL", quantity=5, price=155),
    ]

    # Test add_trades
    result = repo.add_trades(trades)
    assert result == 2
    mock_session.add_all.assert_called_once_with(trades)
    mock_session.commit.assert_called_once()


@patch("backend.src.data_acess.repository.Session")
def test_delete_stock_prices(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    # Mock the delete result
    mock_result = MagicMock()
    mock_result.rowcount = 3
    mock_session.exec.return_value = mock_result

    # Test delete_stock_prices
    result = repo.delete_stock_prices("AAPL")
    assert result == 3
    mock_session.commit.assert_called_once()


@patch("backend.src.data_acess.repository.Session")
def test_delete_trade_data(mock_session_class):
    mock_engine = MagicMock()
    repo = TradeDataRepository(mock_engine)

    # Mock the session context manager
    mock_session = MagicMock()
    mock_session_class.return_value.__enter__.return_value = mock_session
    mock_session_class.return_value.__exit__.return_value = None

    # Mock the delete result
    mock_result = MagicMock()
    mock_result.rowcount = 2
    mock_session.exec.return_value = mock_result

    # Test delete_trade_data
    result = repo.delete_trade_data("AAPL")
    assert result == 2
    mock_session.commit.assert_called_once()
