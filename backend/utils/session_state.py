"""
Session state management utilities for Streamlit.

Handles initialization, chart storage, and rendering of visualizations.
"""

import streamlit as st


def initialize_session_state() -> None:
    """
    Initialize Streamlit session state for messages and charts.

    Creates 'messages' and 'charts' lists in session state if they don't exist.
    Called at application startup.

    Args:
        None

    Returns:
        None
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "charts" not in st.session_state:
        st.session_state.charts = []


def clear_charts() -> None:
    """
    Clear all stored charts from session state.

    Resets the charts list to empty, typically called before generating
    a new agent response.

    Args:
        None

    Returns:
        None
    """
    if "charts" in st.session_state:
        st.session_state.charts = []


def render_charts() -> None:
    """
    Render all charts stored in session state.

    Displays each chart using Plotly in Streamlit with full container width.
    Called after agent response to show generated visualizations.

    Args:
        None

    Returns:
        None
    """
    if "charts" in st.session_state and st.session_state.charts:
        for chart in st.session_state.charts:
            st.plotly_chart(chart, use_container_width=True)
