"""
Financial analyst agent configuration.

Creates and configures the LangChain agent with financial analysis tools
and appropriate system prompts.
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool, StructuredTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, Any

from backend.tools import (
    get_stock_price,
    get_stock_fundamentals,
    get_company_info,
    get_company_news,
    compare_stocks,
    plot_stock_price,
    plot_multiple_stocks,
    plot_volume
)


def create_financial_agent(api_key: str) -> AgentExecutor:
    """
    Create LangChain agent with financial analysis tools.

    Initializes a GPT-4o-mini based agent equipped with 8 financial tools for
    stock analysis, company research, comparisons, and visualizations. The agent
    uses a specialized system prompt defining its role as a financial analyst.

    Args:
        api_key: OpenAI API key for authentication

    Returns:
        AgentExecutor configured with financial tools, LLM, and system prompt,
        ready to process user queries about stocks and markets
    """
    # Wrapper functions for visualization tools that return dict
    # These preserve the full dict while showing only the message to the LLM
    def plot_price_wrapper(ticker: str, period: str = "6mo") -> Dict[str, Any]:
        """Wrapper for plot_stock_price that preserves dict return."""
        return plot_stock_price(ticker, period)

    def plot_multi_wrapper(tickers: str, period: str = "6mo") -> Dict[str, Any]:
        """Wrapper for plot_multiple_stocks that preserves dict return."""
        return plot_multiple_stocks(tickers, period)

    def plot_vol_wrapper(ticker: str, period: str = "3mo") -> Dict[str, Any]:
        """Wrapper for plot_volume that preserves dict return."""
        return plot_volume(ticker, period)

    # Define tools with descriptions
    tools = [
        Tool(
            name="get_stock_price",
            func=get_stock_price,
            description="Get current stock price and basic information. Input should be a stock ticker symbol (e.g., 'AAPL')"
        ),
        Tool(
            name="get_stock_fundamentals",
            func=get_stock_fundamentals,
            description="Get detailed fundamental analysis including P/E ratios, profitability metrics, growth rates. Input should be a stock ticker."
        ),
        Tool(
            name="get_company_news",
            func=get_company_news,
            description="Get recent news articles about a company. Input should be a stock ticker."
        ),
        Tool(
            name="get_company_info",
            func=get_company_info,
            description="Get company description, sector, industry, and business overview. Input should be a stock ticker."
        ),
        Tool(
            name="compare_stocks",
            func=compare_stocks,
            description="Compare multiple stocks side by side. Input should be comma-separated tickers (e.g., 'AAPL,MSFT,GOOGL')"
        ),
        StructuredTool.from_function(
            func=plot_price_wrapper,
            name="plot_stock_price",
            description="Create a candlestick price chart for a stock. Input: 'TICKER' or 'TICKER,PERIOD' where period is 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. Example: 'AAPL,1y' for Apple's 1-year chart.",
            return_direct=False
        ),
        StructuredTool.from_function(
            func=plot_multi_wrapper,
            name="plot_multiple_stocks",
            description="Create a comparison chart showing multiple stocks' performance. Input: comma-separated tickers with optional period at end. Example: 'AAPL,MSFT,GOOGL,6mo' shows 6-month comparison.",
            return_direct=False
        ),
        StructuredTool.from_function(
            func=plot_vol_wrapper,
            name="plot_volume",
            description="Create a trading volume chart for a stock. Input: 'TICKER' or 'TICKER,PERIOD'. Example: 'TSLA,3mo' for Tesla's 3-month volume.",
            return_direct=False
        )
    ]

    # Create LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=api_key
    )

    # Create prompt with system message and placeholders
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert financial analyst assistant. You help users analyze stocks,
        understand market trends, and make informed investment decisions.

        When analyzing stocks:
        - Always fetch relevant data using the available tools
        - Provide clear, actionable insights
        - Highlight both opportunities and risks
        - Compare to industry peers when relevant
        - Be objective and data-driven
        - Create visualizations when users ask to "see", "show", "plot", or "chart" data

        For visualizations:
        - Use plot_stock_price for single stock price charts
        - Use plot_multiple_stocks to compare multiple stocks' performance
        - Use plot_volume to show trading volume
        - When user asks to "compare" stocks visually, use plot_multiple_stocks
        - IMPORTANT: Charts will be displayed automatically below your response
        - DO NOT include markdown images, chart placeholders, or ![...] syntax in your response
        - DO NOT try to embed or reference charts in your text - they appear automatically

        Response formatting:
        - Keep responses natural, concise, and to the point
        - DO NOT use markdown headers (# or ##) in your responses
        - Use plain text with bullet points for lists
        - Avoid verbose explanations - be direct and informative
        - When a chart is created, simply describe what insights it shows without referencing the chart itself

        For stock tickers, always use uppercase (e.g., AAPL not aapl).
        If the user mentions a company name, convert it to its ticker symbol first.

        Available time periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    # Create agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True  # Enable intermediate steps in response
    )

    return agent_executor
