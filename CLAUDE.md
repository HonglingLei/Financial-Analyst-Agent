# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered financial research assistant using LangChain's agent framework with OpenAI LLM. Users query stock data through natural language, and the agent autonomously selects and executes appropriate tools to fetch real-time market data from Yahoo Finance.

**Live Demo**: https://financial-analyst-agent.streamlit.app/

## Development Commands

### Running the Application

**Chainlit Interface:**
```bash
# Activate the project virtual environment
source .venv/bin/activate

# Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run Chainlit app
chainlit run chainlit_app.py
```

The app will open at `http://localhost:8000`

**Alternative - Dev Container:**
```bash
# Run with dev container
# Configured in .devcontainer/devcontainer.json
```

### Environment Setup

- **Python Version**: 3.11.13
- **Virtual Environment**: `.venv/` managed by `uv`
- **Package Manager**: `uv` (fast Python package installer)
- **Package Definition**: `pyproject.toml` with `uv.lock` for reproducible builds
- **Required API Key**: OpenAI API key (provided by users via Chainlit UI prompt)

**Installing/Updating Dependencies:**
```bash
# Install from lock file (recommended)
uv sync

# Or install from requirements.txt (legacy)
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Adding New Dependencies:**
```bash
# Add to pyproject.toml and regenerate lock
uv add package-name
uv lock
```

## Code Style Guidelines

### Python Modules

1. **Function spacing**: Use two empty lines between functions in `.py` modules
2. **Documentation**: All functions must include:
   - Type hints for parameters and return values
   - Brief comment describing what the function does
   - Description of inputs and outputs
3. **Quotation marks**: Always use double quotes by default; single quotes only for nested quotations

Example:

```python
def get_stock_price(ticker: str) -> float:
    """
    Fetches the current stock price for the given ticker.

    Args:
    - ticker: stock ticker

    Returns:
    - xx: xx
    """
    # implementation
    pass
```

## Architecture

### Current Structure (Modularized)

The application has been refactored into a modular structure:

**Backend (`backend/`):**
1. **Tools (`backend/tools/`)**: Financial data fetching functions
   - `stock_data.py`: Price and fundamental data (yfinance)
   - `company_info.py`: Company information and news
   - `comparison.py`: Multi-stock comparison
   - `visualization.py`: Plotly charts (candlestick, performance, volume)
     - Returns `dict` with `{"message": str, "figure": go.Figure}` for Chainlit integration

2. **Agent (`backend/agent/`)**: LangChain agent configuration
   - `financial_agent.py`: Agent setup with GPT-4o-mini
   - Wraps tools and defines system prompt
   - Tool selection logic (autonomous)

3. **Utils (`backend/utils/`)**: Helper functions
   - `chainlit_helpers.py`: Extract charts from agent responses
   - `session_state.py`: Legacy Streamlit state management

**Frontend:**
- **`chainlit_app.py`** (~150 lines): Chainlit interface with native chart persistence and async architecture

### Key Features

**Chainlit Interface:**
- ✅ Native LangChain integration
- ✅ Automatic chart persistence (no manual state management)
- ✅ No page refresh disruptions
- ✅ Async architecture for better performance
- ✅ 8 categorized starter examples
- ✅ Clean, conversational UI

### Agent Pattern Flow

```
User Query → LangChain Agent (GPT-4o-mini)
    ↓
Agent selects tool(s) to call
    ↓
Tool executes (fetches data from yfinance API)
    ↓
Agent synthesizes results into natural language response
    ↓
UI displays response + any generated charts
```

### Key Technical Decisions

- **Modularization**: Refactored from single file to modular structure for better testing and maintainability
- **Chart persistence**: Charts displayed as Chainlit message elements with automatic persistence
- **Visualization tools**: Return `dict[str, Any]` with `"message"` and `"figure"` keys for clean integration
- **Chat history**: Stored as LangChain's `HumanMessage`/`AIMessage` format in session state
- **Tool selection**: Agent autonomously decides tool calls; no hardcoded routing logic
- **Async architecture**: Full async support for better performance and scalability

## Data Sources

- **Market Data**: Yahoo Finance via `yfinance` library
- **Real-time**: Price data, fundamentals, news are fetched live (not cached)
- **No database**: Stateless application, no persistent storage

## Testing

The modular structure enables comprehensive testing:
- `tests/` - Unit tests for backend tools
- Test coverage for all 8 financial analysis tools
- Mock yfinance responses for deterministic testing
- Separate UI and business logic for easier testing

## Important Constraints

- **Educational purpose only**: Not financial advice (noted in UI disclaimer)
- **API Rate Limits**: Yahoo Finance may throttle excessive requests
- **No authentication**: Users provide their own OpenAI API keys; no server-side key management
- **Ticker format**: Always uppercase (e.g., AAPL, MSFT, TSLA)

## Common User Query Patterns

The agent handles:
- Single stock analysis: "Analyze Apple's fundamentals"
- Comparisons: "Compare NVDA vs AMD"
- News: "What's the latest news on Tesla?"
- Visualizations: "Show me Tesla's price chart over the last year" or "Plot AAPL vs MSFT"
- Time periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
