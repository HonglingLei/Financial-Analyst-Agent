"""Tests for stock data tools."""

import pytest
from backend.tools.stock_data import get_stock_price, get_stock_fundamentals


def test_get_stock_price_valid_ticker():
    """Test fetching price for valid ticker."""
    result = get_stock_price("AAPL")
    assert "AAPL" in result or "Apple" in result
    assert "$" in result


def test_get_stock_price_invalid_ticker():
    """Test error handling for invalid ticker."""
    result = get_stock_price("INVALID123")
    # Should either return error message or handle gracefully
    assert isinstance(result, str)


def test_get_stock_fundamentals_valid_ticker():
    """Test fetching fundamentals for valid ticker."""
    result = get_stock_fundamentals("MSFT")
    assert "MSFT" in result
    assert "P/E Ratio" in result or "Profit Margin" in result


def test_get_stock_fundamentals_invalid_ticker():
    """Test error handling for invalid ticker in fundamentals."""
    result = get_stock_fundamentals("INVALID123")
    # Should either return error message or handle gracefully
    assert isinstance(result, str)
