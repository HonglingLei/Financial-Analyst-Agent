"""
Stock visualization tools.

Functions for creating interactive charts including price charts, performance
comparisons, and trading volume visualizations using Plotly.
"""

from typing import Dict, Any
import yfinance as yf
import plotly.graph_objects as go

# Global storage for charts (will be used by Chainlit)
_chart_storage = []


def clear_chart_storage():
    """Clear the global chart storage."""
    global _chart_storage
    _chart_storage = []


def get_stored_charts():
    """Get all stored charts and clear storage."""
    global _chart_storage
    charts = _chart_storage.copy()
    _chart_storage = []
    return charts


def plot_stock_price(ticker: str, period: str = "6mo") -> Dict[str, Any]:
    """
    Create a candlestick price chart for a stock.

    Generates an interactive candlestick chart showing open, high, low, and close
    prices over the specified time period. Returns both the figure and a message.

    Args:
        ticker: Stock ticker symbol or 'TICKER,PERIOD' format (e.g., "AAPL" or "AAPL,1y")
        period: Time period for chart (default "6mo"). Valid: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

    Returns:
        Dictionary with 'message' (str) and 'figure' (plotly.graph_objects.Figure) keys,
        or dictionary with only 'message' key if chart creation fails
    """
    try:
        parts = ticker.split(",")
        ticker_symbol = parts[0].strip().upper()
        period_str = parts[1].strip() if len(parts) > 1 else period

        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period_str)

        if hist.empty:
            return {"message": f"No price data found for {ticker_symbol}"}

        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index,
            open=hist["Open"],
            high=hist["High"],
            low=hist["Low"],
            close=hist["Close"],
            name=ticker_symbol
        )])

        fig.update_layout(
            title=f"{ticker_symbol} Stock Price - {period_str}",
            yaxis_title="Price (USD)",
            xaxis_title="Date",
            template="plotly_white",
            height=500,
            xaxis_rangeslider_visible=False
        )

        # Store figure globally for Chainlit to retrieve
        global _chart_storage
        _chart_storage.append(fig)

        return {
            "message": f"Created price chart for {ticker_symbol} over {period_str}. The chart shows opening, high, low, and closing prices.",
            "figure": fig
        }

    except Exception as e:
        return {"message": f"Error creating price chart: {str(e)}"}


def plot_multiple_stocks(tickers: str, period: str = "6mo") -> Dict[str, Any]:
    """
    Create a comparison chart showing multiple stocks' performance.

    Generates an interactive line chart comparing percentage returns of multiple
    stocks from the start of the period. All stocks are normalized to 0% at the
    start for easy comparison.

    Args:
        tickers: Comma-separated tickers with optional period at end (e.g., "AAPL,MSFT,GOOGL" or "AAPL,MSFT,GOOGL,1y")
        period: Time period for chart (default "6mo"). Valid: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

    Returns:
        Dictionary with 'message' (str) and 'figure' (plotly.graph_objects.Figure) keys,
        or dictionary with only 'message' key if chart creation fails
    """
    try:
        parts = [p.strip() for p in tickers.split(",")]

        # Check if last part is a period
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
        if parts[-1] in valid_periods:
            period_str = parts[-1]
            ticker_list = [t.upper() for t in parts[:-1]]
        else:
            period_str = period
            ticker_list = [t.upper() for t in parts]

        if len(ticker_list) < 2:
            return {"message": "Please provide at least 2 tickers"}

        fig = go.Figure()

        for ticker in ticker_list:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period_str)

            if not hist.empty:
                # Normalize to percentage change from first day
                normalized = (hist["Close"] / hist["Close"].iloc[0] - 1) * 100

                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=normalized,
                    mode="lines",
                    name=ticker,
                    line=dict(width=2)
                ))

        fig.update_layout(
            title=f"Stock Performance Comparison - {period_str}",
            yaxis_title="Return (%)",
            xaxis_title="Date",
            template="plotly_white",
            height=500,
            hovermode="x unified"
        )

        # Store figure globally for Chainlit to retrieve
        global _chart_storage
        _chart_storage.append(fig)

        return {
            "message": f"Created comparison chart for {', '.join(ticker_list)} over {period_str}. Shows percentage return from start of period.",
            "figure": fig
        }

    except Exception as e:
        return {"message": f"Error creating comparison chart: {str(e)}"}


def plot_volume(ticker: str, period: str = "3mo") -> Dict[str, Any]:
    """
    Create a trading volume chart for a stock.

    Generates an interactive bar chart showing daily trading volume over the
    specified period. Bars are colored green for up days (close > open) and
    red for down days.

    Args:
        ticker: Stock ticker symbol or 'TICKER,PERIOD' format (e.g., "AAPL" or "AAPL,6mo")
        period: Time period for chart (default "3mo"). Valid: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

    Returns:
        Dictionary with 'message' (str) and 'figure' (plotly.graph_objects.Figure) keys,
        or dictionary with only 'message' key if chart creation fails
    """
    try:
        parts = ticker.split(",")
        ticker_symbol = parts[0].strip().upper()
        period_str = parts[1].strip() if len(parts) > 1 else period

        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period_str)

        if hist.empty:
            return {"message": f"No volume data found for {ticker_symbol}"}

        fig = go.Figure()

        # Color bars based on price change
        colors = ["red" if row["Close"] < row["Open"] else "green" for _, row in hist.iterrows()]

        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist["Volume"],
            name="Volume",
            marker_color=colors
        ))

        fig.update_layout(
            title=f"{ticker_symbol} Trading Volume - {period_str}",
            yaxis_title="Volume",
            xaxis_title="Date",
            template="plotly_white",
            height=400
        )

        # Store figure globally for Chainlit to retrieve
        global _chart_storage
        _chart_storage.append(fig)

        avg_volume = hist["Volume"].mean()
        return {
            "message": f"Created volume chart for {ticker_symbol} over {period_str}. Average daily volume: {avg_volume:,.0f} shares.",
            "figure": fig
        }

    except Exception as e:
        return {"message": f"Error creating volume chart: {str(e)}"}
