"""Tests for company information tools."""

import pytest
from backend.tools.company_info import get_company_news, get_company_info


def test_get_company_news_valid_ticker():
    """Test fetching news for valid ticker."""
    result = get_company_news("AAPL")
    assert "AAPL" in result
    # Should contain either news items or "No recent news found"
    assert isinstance(result, str)


def test_get_company_news_invalid_ticker():
    """Test error handling for invalid ticker in news fetch."""
    result = get_company_news("INVALID123")
    assert isinstance(result, str)


def test_get_company_info_valid_ticker():
    """Test fetching company info for valid ticker."""
    result = get_company_info("MSFT")
    assert "MSFT" in result
    assert "Company Overview" in result or "Sector" in result


def test_get_company_info_invalid_ticker():
    """Test error handling for invalid ticker in company info."""
    result = get_company_info("INVALID123")
    assert isinstance(result, str)
