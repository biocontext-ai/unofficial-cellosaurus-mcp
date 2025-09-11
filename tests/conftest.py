"""Test configuration for Cellosaurus MCP server."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastmcp import FastMCP


@pytest.fixture
def mock_mcp_app():
    """Create a mock MCP instance for testing."""
    mock_app = MagicMock()
    mock_app.name = "Test MCP App"

    # Create proper mocks for tools with string names
    tool_mock = MagicMock()
    tool_mock.name = "test_tool"
    mock_app.get_tools = AsyncMock(return_value={"test_tool": tool_mock})

    # Create a resource mock with name attribute set to None to match the application behavior
    resource_mock = MagicMock()
    resource_mock.name = None
    mock_app.get_resources = AsyncMock(return_value={"test_resource": resource_mock})

    # Create template mock with string name
    template_mock = MagicMock()
    template_mock.name = "test_template"
    mock_app.get_resource_templates = AsyncMock(return_value={"test_template": template_mock})

    mock_app.import_server = AsyncMock()
    mock_app.http_app = MagicMock(return_value=MagicMock())
    return mock_app


@pytest.fixture
def mock_cellosaurus_client():
    """Create a mock Cellosaurus client for testing."""
    mock_client = MagicMock()
    mock_client.search_cell_lines = AsyncMock()
    mock_client.get_cell_line = AsyncMock()
    mock_client.get_release_info = AsyncMock()
    return mock_client


@pytest.fixture
def fastmcp_instance():
    """Create a FastMCP instance for testing."""
    return FastMCP(
        name="Test Cellosaurus MCP",
        instructions="Test MCP server for Cellosaurus",
    )
