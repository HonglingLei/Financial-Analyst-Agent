"""
Stock data retrieval tools.

Functions for fetching current stock prices and fundamental analysis metrics
from Yahoo Finance.
"""

import yfinance as yf


def get_stock_price(ticker: str) -> str:
    """
    Get current stock price and basic information.

    Fetches real-time price, price change, market cap, and 52-week range
    for the specified stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Formatted string containing current price, change, market cap,
        and 52-week range, or error message if fetch fails
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get("currentPrice", info.get("regularMarketPrice", 0))
        prev_close = info.get("previousClose", current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        return f"""
{info.get("longName", ticker)} ({ticker.upper()})
Current Price: ${current_price:.2f}
Change: ${change:+.2f} ({change_pct:+.2f}%)
Market Cap: ${info.get("marketCap", 0)/1e9:.2f}B
52W Range: ${info.get("fiftyTwoWeekLow", 0):.2f} - ${info.get("fiftyTwoWeekHigh", 0):.2f}
"""
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"


def get_stock_fundamentals(ticker: str) -> str:
    """
    Get detailed fundamental analysis metrics.

    Fetches comprehensive fundamental data including valuation ratios,
    profitability metrics, growth rates, financial health indicators,
    and analyst recommendations.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL")

    Returns:
        Formatted string containing fundamental metrics organized by category
        (valuation, profitability, growth, financial health, analyst info),
        or error message if fetch fails
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return f"""
Fundamental Analysis for {ticker.upper()}:

Valuation Metrics:
- P/E Ratio: {info.get("trailingPE", "N/A")}
- Forward P/E: {info.get("forwardPE", "N/A")}
- PEG Ratio: {info.get("pegRatio", "N/A")}
- Price/Book: {info.get("priceToBook", "N/A")}
- Price/Sales: {info.get("priceToSalesTrailing12Months", "N/A")}

Profitability:
- Profit Margin: {info.get("profitMargins", 0)*100:.2f}%
- Operating Margin: {info.get("operatingMargins", 0)*100:.2f}%
- ROE: {info.get("returnOnEquity", 0)*100:.2f}%
- ROA: {info.get("returnOnAssets", 0)*100:.2f}%

Growth:
- Revenue Growth: {info.get("revenueGrowth", 0)*100:.2f}%
- Earnings Growth: {info.get("earningsGrowth", 0)*100:.2f}%

Financial Health:
- Total Revenue: ${info.get("totalRevenue", 0)/1e9:.2f}B
- Free Cash Flow: ${info.get("freeCashflow", 0)/1e9:.2f}B
- Debt/Equity: {info.get("debtToEquity", "N/A")}
- Current Ratio: {info.get("currentRatio", "N/A")}

Analyst Info:
- Recommendation: {info.get("recommendationKey", "N/A").upper()}
- Target Price: ${info.get("targetMeanPrice", "N/A")}
"""
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"
