"""
Chainlit interface for Financial Analysis Agent.

Main entry point for the Chainlit-based chat interface. Provides a conversational
UI for financial analysis with native LangChain integration and automatic chart
persistence.
"""

import os
import chainlit as cl
from langchain_core.messages import HumanMessage, AIMessage

from backend.agent import create_financial_agent
from backend.tools import get_stored_charts, clear_chart_storage


@cl.set_starters
async def set_starters():
    """
    Define example starter prompts for users.

    Provides 8 categorized examples covering all agent capabilities:
    single stock analysis, comparisons, and visualizations.

    Returns:
        List of Chainlit Starter objects displayed in the UI
    """
    return [
        cl.Starter(
            label="📊 Analyze Apple's Fundamentals",
            message="Analyze Apple's stock fundamentals including P/E ratio, profit margins, and growth metrics"
        ),
        cl.Starter(
            label="📈 Compare Tech Giants",
            message="Compare AAPL, MSFT, and GOOGL performance over the last year with a chart"
        ),
        cl.Starter(
            label="📰 Latest Tesla News",
            message="What's the latest news about Tesla (TSLA)?"
        ),
        cl.Starter(
            label="💰 Get NVIDIA Price",
            message="What is NVIDIA's current stock price?"
        ),
        cl.Starter(
            label="📉 Tesla Price Chart",
            message="Show me Tesla's stock price chart for the last 6 months"
        ),
        cl.Starter(
            label="🏢 Company Info",
            message="Tell me about Microsoft - what sector are they in and what do they do?"
        ),
        cl.Starter(
            label="📊 Volume Analysis",
            message="Show me the trading volume for AMD over the past 3 months"
        ),
        cl.Starter(
            label="⚖️ Compare Semiconductors",
            message="Compare the fundamentals of NVDA and AMD side by side"
        )
    ]


@cl.on_chat_start
async def start():
    """
    Initialize chat session with welcome message and agent setup.

    Displays welcome message explaining agent capabilities, checks for OpenAI
    API key, and creates the financial agent. Initializes empty chat history
    in session state.

    Returns:
        None
    """
    # Send welcome message
    welcome_message = """# Financial Analysis Agent

Welcome! I'm an AI-powered financial analyst that can help you with:

- **Real-time Stock Data**: Current prices, market cap, and key metrics
- **Fundamental Analysis**: P/E ratios, profit margins, growth rates, and more
- **Company Information**: Business overview, sector, industry details
- **News & Updates**: Latest news articles about companies
- **Stock Comparisons**: Side-by-side analysis of multiple stocks
- **Interactive Charts**: Price charts, performance comparisons, volume analysis

**Disclaimer**: This is for educational purposes only and not financial advice.

Now, try asking me something about stocks, companies, or markets!
"""
    await cl.Message(content=welcome_message).send()

    # Get OpenAI API key from Chainlit's user environment
    user_env = cl.user_session.get("env")
    api_key = user_env.get("OPENAI_API_KEY") if user_env else None

    # Fallback to system environment if not provided by user
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        await cl.Message(
            content="⚠️ **OpenAI API Key Required**\n\nPlease refresh the page and enter your OpenAI API key when prompted."
        ).send()
        return

    # Create financial agent
    try:
        agent = create_financial_agent(api_key)
        cl.user_session.set("agent", agent)
        cl.user_session.set("chat_history", [])

    except Exception as e:
        await cl.Message(
            content=f"❌ **Error initializing agent**: {str(e)}\n\nPlease check your API key and try again."
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages and generate agent responses.

    Processes user query through the LangChain agent, extracts any generated
    charts, updates chat history, and sends response with inline visualizations.

    Args:
        message: Chainlit Message object containing user input

    Returns:
        None
    """
    # Get agent and chat history from session
    agent = cl.user_session.get("agent")
    chat_history = cl.user_session.get("chat_history", [])

    if not agent:
        await cl.Message(
            content="⚠️ Agent not initialized. Please restart the chat."
        ).send()
        return

    # Clear any previous charts
    clear_chart_storage()

    # Show processing indicator
    async with cl.Step(name="Agent Execution", type="llm") as step:
        step.input = message.content

        try:
            # Invoke agent with user query and chat history
            response = await cl.make_async(agent.invoke)({
                "input": message.content,
                "chat_history": chat_history
            })

            # Extract output
            output_text = response.get("output", "No response generated.")

            # Format intermediate steps for display
            intermediate_steps = response.get("intermediate_steps", [])
            if intermediate_steps:
                # Tool descriptions for task field
                tool_descriptions = {
                    "get_stock_price": "Fetch current stock price and basic metrics",
                    "get_stock_fundamentals": "Retrieve fundamental analysis data",
                    "get_company_info": "Get company overview and business details",
                    "get_company_news": "Fetch recent news articles",
                    "compare_stocks": "Compare multiple stocks side-by-side",
                    "plot_stock_price": "Generate candlestick price chart",
                    "plot_multiple_stocks": "Create performance comparison chart",
                    "plot_volume": "Generate trading volume chart"
                }

                steps_summary = ["**Tool Execution Steps:**\n"]
                for i, step_item in enumerate(intermediate_steps, 1):
                    if len(step_item) >= 2:
                        action, output = step_item[0], step_item[1]

                        # Extract tool info
                        tool_name = getattr(action, 'tool', 'unknown')
                        tool_input = getattr(action, 'tool_input', '')
                        task_description = tool_descriptions.get(tool_name, "Execute tool operation")

                        # Format input nicely (limit to 100 chars)
                        if isinstance(tool_input, dict):
                            input_str = ", ".join(f"{k}={v}" for k, v in tool_input.items())
                        else:
                            input_str = str(tool_input)
                        input_display = input_str[:100] + '...' if len(input_str) > 100 else input_str

                        # Get output (limit to 150 chars)
                        if isinstance(output, dict) and 'message' in output:
                            output_display = output['message']
                        else:
                            output_display = str(output)
                        output_display = output_display[:150] + '...' if len(output_display) > 150 else output_display

                        # Build step display with task, input, output
                        step_text = (
                            f"\n**Step {i}:** {tool_name}\n"
                            f"**Task:** {task_description}\n"
                            f"**Input:** `{input_display}`\n"
                            f"**Output:** {output_display}"
                        )

                        # Add separation line if not the last step
                        if i < len(intermediate_steps):
                            step_text += "\n\n---"

                        steps_summary.append(step_text)

                step.output = "\n".join(steps_summary)
            else:
                step.output = "ℹ️ No tools were called - agent responded directly from knowledge."

        except Exception as e:
            error_message = f"❌ **Error processing request**: {str(e)}"
            await cl.Message(content=error_message).send()
            return

    # Get charts that were stored during tool execution
    charts = get_stored_charts()

    # Update chat history
    chat_history.extend([
        HumanMessage(content=message.content),
        AIMessage(content=output_text)
    ])
    cl.user_session.set("chat_history", chat_history)

    # Create chart elements for display
    elements = [
        cl.Plotly(name=f"chart_{i}", figure=fig)
        for i, fig in enumerate(charts)
    ]

    # Send response with charts
    await cl.Message(
        content=output_text,
        elements=elements if elements else None
    ).send()
