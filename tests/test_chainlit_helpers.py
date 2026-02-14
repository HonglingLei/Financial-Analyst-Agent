"""
Tests for Chainlit helper functions.

Verifies that chart extraction from LangChain agent responses works correctly.
"""

import plotly.graph_objects as go
from backend.utils.chainlit_helpers import extract_charts_from_response


def test_extract_charts_from_response_with_charts():
    """
    Test extracting Plotly figures from agent response with charts.

    Ensures that figures are correctly extracted from intermediate steps
    when tools return dict responses with 'figure' keys.

    Args:
        None

    Returns:
        None
    """
    # Create a mock Plotly figure
    fig = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])])

    # Mock agent response with intermediate steps
    agent_response = {
        "output": "Created chart successfully",
        "intermediate_steps": [
            (
                {"tool": "plot_stock_price", "tool_input": "AAPL"},
                {"message": "Created price chart for AAPL", "figure": fig}
            )
        ]
    }

    # Extract charts
    charts = extract_charts_from_response(agent_response)

    # Verify
    assert len(charts) == 1
    assert isinstance(charts[0], go.Figure)
    assert charts[0] == fig


def test_extract_charts_from_response_without_charts():
    """
    Test extracting charts when no charts are present.

    Ensures function returns empty list when agent response contains
    no visualization tool outputs.

    Args:
        None

    Returns:
        None
    """
    # Mock agent response without charts
    agent_response = {
        "output": "Current price is $150",
        "intermediate_steps": [
            (
                {"tool": "get_stock_price", "tool_input": "AAPL"},
                "Current price: $150.00"
            )
        ]
    }

    # Extract charts
    charts = extract_charts_from_response(agent_response)

    # Verify
    assert len(charts) == 0


def test_extract_charts_from_response_multiple_charts():
    """
    Test extracting multiple Plotly figures from agent response.

    Ensures all figures are extracted when multiple visualization tools
    are called in a single agent execution.

    Args:
        None

    Returns:
        None
    """
    # Create mock Plotly figures
    fig1 = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])
    fig2 = go.Figure(data=[go.Bar(x=[1, 2], y=[5, 6])])

    # Mock agent response with multiple charts
    agent_response = {
        "output": "Created multiple charts",
        "intermediate_steps": [
            (
                {"tool": "plot_stock_price", "tool_input": "AAPL"},
                {"message": "Created price chart", "figure": fig1}
            ),
            (
                {"tool": "plot_volume", "tool_input": "AAPL"},
                {"message": "Created volume chart", "figure": fig2}
            )
        ]
    }

    # Extract charts
    charts = extract_charts_from_response(agent_response)

    # Verify
    assert len(charts) == 2
    assert isinstance(charts[0], go.Figure)
    assert isinstance(charts[1], go.Figure)
    assert charts[0] == fig1
    assert charts[1] == fig2


def test_extract_charts_from_response_empty():
    """
    Test extracting charts from empty agent response.

    Ensures function handles empty or malformed responses gracefully.

    Args:
        None

    Returns:
        None
    """
    # Empty response
    agent_response = {}

    # Extract charts
    charts = extract_charts_from_response(agent_response)

    # Verify
    assert len(charts) == 0
