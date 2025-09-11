"""Real integration tests for Cellosaurus MCP tools."""

import pytest

import cellosaurus_mcp
from cellosaurus_mcp.tools.cellosaurus_tools import (
    find_cell_lines_by_disease,
    find_cell_lines_by_tissue,
    get_cell_line_info,
    get_release_info,
    list_available_fields,
    search_cell_lines,
)


def test_package_has_version():
    """Test that the package has a version."""
    assert cellosaurus_mcp.__version__ is not None


def test_list_available_fields():
    """Test list_available_fields."""
    fields = list_available_fields.fn()  # type: ignore[attr-defined]
    assert isinstance(fields, dict)
    assert "id" in fields
    assert "ac" in fields


class TestRealQueries:
    """Real integration tests that actually call the Cellosaurus API."""

    @pytest.mark.asyncio
    async def test_search_hela_cells(self):
        """Search for HeLa cells."""
        result = await search_cell_lines.fn(  # type: ignore[attr-defined]
            query="id:HeLa", fields=["id", "ac"], rows=5
        )

        assert "error" not in result
        assert "Cellosaurus" in result
        assert "cell-line-list" in result["Cellosaurus"]
        results = result["Cellosaurus"]["cell-line-list"]
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_get_hela_cell_info(self):
        """Get HeLa cell info."""
        result = await get_cell_line_info.fn(accession="CVCL_0030")  # type: ignore[attr-defined]
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_find_cancer_cell_lines(self):
        """Find cancer cell lines."""
        result = await find_cell_lines_by_disease.fn(  # type: ignore[attr-defined]
            disease="cancer", species="human", limit=3
        )
        assert "error" not in result
        assert "Cellosaurus" in result
        assert "cell-line-list" in result["Cellosaurus"]
        results = result["Cellosaurus"]["cell-line-list"]
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_find_liver_cell_lines(self):
        """Find liver cell lines."""
        result = await find_cell_lines_by_tissue.fn(  # type: ignore[attr-defined]
            tissue="liver", species="human", limit=3
        )
        assert "error" not in result
        assert "Cellosaurus" in result
        assert "cell-line-list" in result["Cellosaurus"]
        results = result["Cellosaurus"]["cell-line-list"]
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_get_release_info_basic(self):
        """Get release info."""
        result = await get_release_info.fn()  # type: ignore[attr-defined]
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_search_with_invalid_field(self):
        """Test invalid field error."""
        result = await search_cell_lines.fn(  # type: ignore[attr-defined]
            query="id:HeLa", fields=["invalid_field_name"]
        )
        assert "error" in result
