"""
Company information tools.

Functions for fetching company news, descriptions, and business overviews
from Yahoo Finance.
"""

import yfinance as yf
from datetime import datetime


def get_company_news(ticker: str) -> str:
    """
    Get recent news articles about a company.

    Fetches the top 5 most recent news items for the specified stock,
    including publication date, title, and source.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Formatted string containing recent news items with dates and sources,
        or message indicating no news found, or error message if fetch fails
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:5]  # Get top 5 news items

        if not news:
            return f"No recent news found for {ticker}"

        news_summary = f"Recent News for {ticker.upper()}:\n\n"
        for i, item in enumerate(news, 1):
            published = datetime.fromtimestamp(item.get("providerPublishTime", 0))
            news_summary += f"{i}. [{published.strftime('%Y-%m-%d')}] {item.get('title', '')}\n"
            news_summary += f"   Source: {item.get('publisher', 'Unknown')}\n\n"

        return news_summary
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"


def get_company_info(ticker: str) -> str:
    """
    Get company description and business overview.

    Fetches detailed company information including name, sector, industry,
    country, employee count, business summary, and website.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Formatted string containing company overview information,
        or error message if fetch fails
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return f"""
Company Overview for {ticker.upper()}:

Name: {info.get("longName", ticker)}
Sector: {info.get("sector", "N/A")}
Industry: {info.get("industry", "N/A")}
Country: {info.get("country", "N/A")}
Employees: {info.get("fullTimeEmployees", "N/A"):,}

Business Summary:
{info.get("longBusinessSummary", "No description available")}

Website: {info.get("website", "N/A")}
"""
    except Exception as e:
        return f"Error fetching company info for {ticker}: {str(e)}"
