"""
Stock comparison tools.

Functions for side-by-side comparison of multiple stocks' key metrics.
"""

import yfinance as yf


def compare_stocks(tickers: str) -> str:
    """
    Compare multiple stocks side by side.

    Fetches and compares key financial metrics for multiple stocks including
    current price, market cap, P/E ratio, profit margin, revenue growth, and ROE.
    Displays results in a formatted table.

    Args:
        tickers: Comma-separated stock ticker symbols (e.g., "AAPL,MSFT,GOOGL")

    Returns:
        Formatted table string comparing key metrics across all provided tickers,
        or message requesting more tickers if fewer than 2 provided,
        or error message if fetch fails
    """
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(",")]
        if len(ticker_list) < 2:
            return "Please provide at least 2 tickers separated by commas"

        comparison = "Stock Comparison:\n\n"
        comparison += f"{'Metric':<20} " + " ".join([f"{t:>12}" for t in ticker_list]) + "\n"
        comparison += "-" * (20 + 13 * len(ticker_list)) + "\n"

        data = {}
        for ticker in ticker_list:
            stock = yf.Ticker(ticker)
            data[ticker] = stock.info

        metrics = [
            ("Price", "currentPrice", lambda x: f"${x:.2f}"),
            ("Market Cap", "marketCap", lambda x: f"${x/1e9:.1f}B"),
            ("P/E Ratio", "trailingPE", lambda x: f"{x:.2f}"),
            ("Profit Margin", "profitMargins", lambda x: f"{x*100:.2f}%"),
            ("Revenue Growth", "revenueGrowth", lambda x: f"{x*100:.2f}%"),
            ("ROE", "returnOnEquity", lambda x: f"{x*100:.2f}%"),
        ]

        for label, key, formatter in metrics:
            row = f"{label:<20} "
            for ticker in ticker_list:
                value = data[ticker].get(key, None)
                if value is not None:
                    try:
                        row += f"{formatter(value):>12} "
                    except:
                        row += f"{'N/A':>12} "
                else:
                    row += f"{'N/A':>12} "
            comparison += row + "\n"

        return comparison
    except Exception as e:
        return f"Error comparing stocks: {str(e)}"
