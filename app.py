"""
Financial Analyst Agent - Built with LangChain & Streamlit

Install requirements:
pip install streamlit langchain langchain-openai yfinance pandas plotly python-dotenv

Run:
streamlit run app.py
"""

import streamlit as st
import yfinance as yf
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import re

# Page config
st.set_page_config(
    page_title="Financial Analyst Agent",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ============= TOOL DEFINITIONS =============

def get_stock_price(ticker: str) -> str:
    """Get current stock price and basic info"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return f"""
{info.get('longName', ticker)} ({ticker.upper()})
Current Price: ${current_price:.2f}
Change: ${change:+.2f} ({change_pct:+.2f}%)
Market Cap: ${info.get('marketCap', 0)/1e9:.2f}B
52W Range: ${info.get('fiftyTwoWeekLow', 0):.2f} - ${info.get('fiftyTwoWeekHigh', 0):.2f}
"""
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

def get_stock_fundamentals(ticker: str) -> str:
    """Get detailed fundamental metrics"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return f"""
Fundamental Analysis for {ticker.upper()}:

Valuation Metrics:
- P/E Ratio: {info.get('trailingPE', 'N/A')}
- Forward P/E: {info.get('forwardPE', 'N/A')}
- PEG Ratio: {info.get('pegRatio', 'N/A')}
- Price/Book: {info.get('priceToBook', 'N/A')}
- Price/Sales: {info.get('priceToSalesTrailing12Months', 'N/A')}

Profitability:
- Profit Margin: {info.get('profitMargins', 0)*100:.2f}%
- Operating Margin: {info.get('operatingMargins', 0)*100:.2f}%
- ROE: {info.get('returnOnEquity', 0)*100:.2f}%
- ROA: {info.get('returnOnAssets', 0)*100:.2f}%

Growth:
- Revenue Growth: {info.get('revenueGrowth', 0)*100:.2f}%
- Earnings Growth: {info.get('earningsGrowth', 0)*100:.2f}%

Financial Health:
- Total Revenue: ${info.get('totalRevenue', 0)/1e9:.2f}B
- Free Cash Flow: ${info.get('freeCashflow', 0)/1e9:.2f}B
- Debt/Equity: {info.get('debtToEquity', 'N/A')}
- Current Ratio: {info.get('currentRatio', 'N/A')}

Analyst Info:
- Recommendation: {info.get('recommendationKey', 'N/A').upper()}
- Target Price: ${info.get('targetMeanPrice', 'N/A')}
"""
    except Exception as e:
        return f"Error fetching fundamentals for {ticker}: {str(e)}"

def get_company_news(ticker: str) -> str:
    """Get recent company news"""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news[:5]  # Get top 5 news items
        
        if not news:
            return f"No recent news found for {ticker}"
        
        news_summary = f"Recent News for {ticker.upper()}:\n\n"
        for i, item in enumerate(news, 1):
            published = datetime.fromtimestamp(item.get('providerPublishTime', 0))
            news_summary += f"{i}. [{published.strftime('%Y-%m-%d')}] {item.get('title', '')}\n"
            news_summary += f"   Source: {item.get('publisher', 'Unknown')}\n\n"
        
        return news_summary
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"

def get_company_info(ticker: str) -> str:
    """Get company description and business overview"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return f"""
Company Overview for {ticker.upper()}:

Name: {info.get('longName', ticker)}
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Country: {info.get('country', 'N/A')}
Employees: {info.get('fullTimeEmployees', 'N/A'):,}

Business Summary:
{info.get('longBusinessSummary', 'No description available')}

Website: {info.get('website', 'N/A')}
"""
    except Exception as e:
        return f"Error fetching company info for {ticker}: {str(e)}"

def compare_stocks(tickers: str) -> str:
    """Compare multiple stocks side by side. Input format: 'AAPL,MSFT,GOOGL'"""
    try:
        ticker_list = [t.strip().upper() for t in tickers.split(',')]
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
            ('Price', 'currentPrice', lambda x: f"${x:.2f}"),
            ('Market Cap', 'marketCap', lambda x: f"${x/1e9:.1f}B"),
            ('P/E Ratio', 'trailingPE', lambda x: f"{x:.2f}"),
            ('Profit Margin', 'profitMargins', lambda x: f"{x*100:.2f}%"),
            ('Revenue Growth', 'revenueGrowth', lambda x: f"{x*100:.2f}%"),
            ('ROE', 'returnOnEquity', lambda x: f"{x*100:.2f}%"),
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

def plot_stock_price(ticker: str, period: str = "6mo") -> str:
    """
    Plot stock price over time. 
    Input format: 'AAPL' or 'AAPL,1y' where period can be: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    """
    try:
        parts = ticker.split(',')
        ticker_symbol = parts[0].strip().upper()
        period_str = parts[1].strip() if len(parts) > 1 else period
        
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period_str)
        
        if hist.empty:
            return f"No price data found for {ticker_symbol}"
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name=ticker_symbol
        )])
        
        fig.update_layout(
            title=f'{ticker_symbol} Stock Price - {period_str}',
            yaxis_title='Price (USD)',
            xaxis_title='Date',
            template='plotly_white',
            height=500,
            xaxis_rangeslider_visible=False
        )
        
        # Store chart in session state for display
        if 'charts' not in st.session_state:
            st.session_state.charts = []
        st.session_state.charts.append(fig)
        
        return f"Created price chart for {ticker_symbol} over {period_str}. The chart shows opening, high, low, and closing prices."
    
    except Exception as e:
        return f"Error creating price chart: {str(e)}"

def plot_multiple_stocks(tickers: str, period: str = "6mo") -> str:
    """
    Plot multiple stocks on same chart for comparison.
    Input format: 'AAPL,MSFT,GOOGL' or 'AAPL,MSFT,GOOGL,1y'
    """
    try:
        parts = [p.strip() for p in tickers.split(',')]
        
        # Check if last part is a period
        valid_periods = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']
        if parts[-1] in valid_periods:
            period_str = parts[-1]
            ticker_list = [t.upper() for t in parts[:-1]]
        else:
            period_str = period
            ticker_list = [t.upper() for t in parts]
        
        if len(ticker_list) < 2:
            return "Please provide at least 2 tickers"
        
        fig = go.Figure()
        
        for ticker in ticker_list:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period_str)
            
            if not hist.empty:
                # Normalize to percentage change from first day
                normalized = (hist['Close'] / hist['Close'].iloc[0] - 1) * 100
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=normalized,
                    mode='lines',
                    name=ticker,
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title=f'Stock Performance Comparison - {period_str}',
            yaxis_title='Return (%)',
            xaxis_title='Date',
            template='plotly_white',
            height=500,
            hovermode='x unified'
        )
        
        # Store chart
        if 'charts' not in st.session_state:
            st.session_state.charts = []
        st.session_state.charts.append(fig)
        
        return f"Created comparison chart for {', '.join(ticker_list)} over {period_str}. Shows percentage return from start of period."
    
    except Exception as e:
        return f"Error creating comparison chart: {str(e)}"

def plot_volume(ticker: str, period: str = "3mo") -> str:
    """
    Plot trading volume over time.
    Input format: 'AAPL' or 'AAPL,6mo'
    """
    try:
        parts = ticker.split(',')
        ticker_symbol = parts[0].strip().upper()
        period_str = parts[1].strip() if len(parts) > 1 else period
        
        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period=period_str)
        
        if hist.empty:
            return f"No volume data found for {ticker_symbol}"
        
        fig = go.Figure()
        
        # Color bars based on price change
        colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in hist.iterrows()]
        
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            marker_color=colors
        ))
        
        fig.update_layout(
            title=f'{ticker_symbol} Trading Volume - {period_str}',
            yaxis_title='Volume',
            xaxis_title='Date',
            template='plotly_white',
            height=400
        )
        
        # Store chart
        if 'charts' not in st.session_state:
            st.session_state.charts = []
        st.session_state.charts.append(fig)
        
        avg_volume = hist['Volume'].mean()
        return f"Created volume chart for {ticker_symbol} over {period_str}. Average daily volume: {avg_volume:,.0f} shares."
    
    except Exception as e:
        return f"Error creating volume chart: {str(e)}"

# ============= LANGCHAIN SETUP =============

def create_agent(api_key: str):
    """Create LangChain agent with financial tools"""
    
    # Define tools
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
        Tool(
            name="plot_stock_price",
            func=plot_stock_price,
            description="Create a candlestick price chart for a stock. Input: 'TICKER' or 'TICKER,PERIOD' where period is 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. Example: 'AAPL,1y' for Apple's 1-year chart."
        ),
        Tool(
            name="plot_multiple_stocks",
            func=plot_multiple_stocks,
            description="Create a comparison chart showing multiple stocks' performance. Input: comma-separated tickers with optional period at end. Example: 'AAPL,MSFT,GOOGL,6mo' shows 6-month comparison."
        ),
        Tool(
            name="plot_volume",
            func=plot_volume,
            description="Create a trading volume chart for a stock. Input: 'TICKER' or 'TICKER,PERIOD'. Example: 'TSLA,3mo' for Tesla's 3-month volume."
        )
    ]
    
    # Create LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=api_key
    )
    
    # Create prompt
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
        handle_parsing_errors=True
    )
    
    return agent_executor

# ============= STREAMLIT UI =============

st.title("📊 Financial Analyst Agent")
st.caption("Powered by LangChain & OpenAI | Real-time market data from Yahoo Finance")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", help="Get your key at platform.openai.com")
    
    st.markdown("---")
    st.markdown("### 💡 Analysis Examples")
    st.markdown("""
    - Analyze Apple's fundamentals
    - Compare NVDA vs AMD
    - What's the latest news on Tesla?
    - What's Microsoft's valuation?
    - Compare TSLA, F, GM performance over 6 months
    - What's the trading volume of NVDA?
    - What are the risks for semiconductor stocks?
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Visualization Examples")
    st.markdown("""
    - Show me Tesla's price chart over the last year
    - Plot AAPL vs MSFT vs GOOGL
    - Chart NVDA volume for 3 months
    - Compare tech stocks visually
    """)
    
    st.markdown("---")
    st.markdown("### 📈 Popular Tickers")
    st.markdown("""
    - **Tech:** AAPL, MSFT, GOOGL, META, NVDA, AMD
    - **Auto:** TSLA, F, GM
    - **Finance:** JPM, BAC, GS
    """)
    
    st.markdown("---")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
if not api_key:
    st.warning("⚠️ Please enter your OpenAI API key in the sidebar to start")
    st.info("Don't have an API key? Get one at [platform.openai.com](https://platform.openai.com)")
else:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about stocks, markets, or companies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    # Clear any previous charts for this response
                    if 'charts' in st.session_state:
                        st.session_state.charts = []
                    
                    # Create agent
                    agent = create_agent(api_key)
                    
                    # Prepare chat history for LangChain
                    chat_history = []
                    for msg in st.session_state.messages[:-1]:  # Exclude current message
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        else:
                            chat_history.append(AIMessage(content=msg["content"]))
                    
                    # Run agent
                    response = agent.invoke({
                        "input": prompt,
                        "chat_history": chat_history
                    })
                    
                    # Display response (remove any image markdown syntax)
                    answer = response["output"]
                    # Remove markdown image syntax like ![alt text](path)
                    answer = re.sub(r'!\[.*?\]\(.*?\)', '', answer)
                    st.markdown(answer)
                    
                    # Display any charts that were created
                    if 'charts' in st.session_state and st.session_state.charts:
                        for chart in st.session_state.charts:
                            st.plotly_chart(chart, use_container_width=True)
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}\n\nPlease check your API key and try again."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.caption("⚠️ **Disclaimer:** This tool is for educational purposes only. Not financial advice. Always do your own research before making investment decisions.")