"""Tests for stock comparison tools."""

import pytest
from backend.tools.comparison import compare_stocks


def test_compare_stocks_multiple_tickers():
    """Test comparing multiple valid tickers."""
    result = compare_stocks("AAPL,MSFT,GOOGL")
    assert "Stock Comparison" in result
    assert "AAPL" in result
    assert "MSFT" in result
    assert "GOOGL" in result


def test_compare_stocks_two_tickers():
    """Test comparing two tickers (minimum requirement)."""
    result = compare_stocks("AAPL,MSFT")
    assert "Stock Comparison" in result
    assert "AAPL" in result and "MSFT" in result


def test_compare_stocks_single_ticker():
    """Test error handling for single ticker."""
    result = compare_stocks("AAPL")
    assert "at least 2 tickers" in result


def test_compare_stocks_empty_string():
    """Test error handling for empty input."""
    result = compare_stocks("")
    # Should request more tickers or return error
    assert isinstance(result, str)
