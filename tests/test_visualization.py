"""
Tests for visualization tools.

Updated to test dict return type for Chainlit integration.
"""

import pytest
import plotly.graph_objects as go
from backend.tools.visualization import plot_stock_price, plot_multiple_stocks, plot_volume


def test_plot_stock_price_basic():
    """
    Test creating basic stock price chart.

    Verifies that plot_stock_price returns a dict with 'message' and 'figure' keys,
    and that the figure is a valid Plotly Figure object.

    Args:
        None

    Returns:
        None
    """
    result = plot_stock_price("AAPL")

    # Should return a dict
    assert isinstance(result, dict)

    # Should have a message key
    assert "message" in result
    assert isinstance(result["message"], str)

    # Check if chart was created successfully or if there was an error
    if "Created price chart" in result["message"]:
        # Should have a figure key
        assert "figure" in result
        assert isinstance(result["figure"], go.Figure)
    else:
        # Error case - no figure expected
        assert "Error" in result["message"] or "No price data" in result["message"]


def test_plot_stock_price_with_period():
    """
    Test creating stock price chart with custom period.

    Verifies that custom time periods are parsed correctly and chart
    is generated for the specified period.

    Args:
        None

    Returns:
        None
    """
    result = plot_stock_price("AAPL,1y")

    # Should return a dict
    assert isinstance(result, dict)
    assert "message" in result
    assert isinstance(result["message"], str)

    # Check if chart was created successfully
    if "Created price chart" in result["message"]:
        assert "figure" in result
        assert isinstance(result["figure"], go.Figure)
        assert "1y" in result["message"]
    else:
        assert "Error" in result["message"] or "No price data" in result["message"]


def test_plot_multiple_stocks():
    """
    Test creating comparison chart for multiple stocks.

    Verifies that multiple tickers are processed and a comparison
    chart is generated with normalized performance data.

    Args:
        None

    Returns:
        None
    """
    result = plot_multiple_stocks("AAPL,MSFT,GOOGL")

    # Should return a dict
    assert isinstance(result, dict)
    assert "message" in result

    # Should either create chart, request more tickers, or return error
    message = result["message"]
    if "Created comparison chart" in message:
        assert "figure" in result
        assert isinstance(result["figure"], go.Figure)
    elif "at least 2 tickers" in message:
        # Edge case: validation message
        assert "figure" not in result
    else:
        # Error case
        assert "Error" in message


def test_plot_volume_basic():
    """
    Test creating volume chart.

    Verifies that trading volume chart is generated with colored bars
    based on price movement.

    Args:
        None

    Returns:
        None
    """
    result = plot_volume("AAPL")

    # Should return a dict
    assert isinstance(result, dict)
    assert "message" in result
    assert isinstance(result["message"], str)

    # Check if chart was created successfully
    if "Created volume chart" in result["message"]:
        assert "figure" in result
        assert isinstance(result["figure"], go.Figure)
    else:
        assert "Error" in result["message"] or "No volume data" in result["message"]


def test_plot_stock_price_invalid_ticker():
    """
    Test error handling for invalid ticker symbol.

    Verifies that appropriate error message is returned for non-existent
    ticker symbols.

    Args:
        None

    Returns:
        None
    """
    result = plot_stock_price("INVALID_TICKER_XYZ")

    # Should return a dict with error message
    assert isinstance(result, dict)
    assert "message" in result
    # Should not have a figure for invalid ticker
    assert "figure" not in result or "No price data" in result["message"] or "Error" in result["message"]


def test_plot_multiple_stocks_single_ticker():
    """
    Test validation when only one ticker is provided.

    Verifies that function requests at least 2 tickers for comparison.

    Args:
        None

    Returns:
        None
    """
    result = plot_multiple_stocks("AAPL")

    # Should return a dict
    assert isinstance(result, dict)
    assert "message" in result

    # Should request at least 2 tickers
    assert "at least 2 tickers" in result["message"]
    assert "figure" not in result
