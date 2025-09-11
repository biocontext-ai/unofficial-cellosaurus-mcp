"""Tests for Cellosaurus MCP server functionality."""

from unittest.mock import AsyncMock, patch

import pytest

import cellosaurus_mcp
from cellosaurus_mcp.client import CellosaurusClient, client
from cellosaurus_mcp.models import CellLineRequest, CellosaurusField, Format, SearchRequest


async def _search_cell_lines_helper(
    query: str = "id:HeLa", fields=None, start: int = 0, rows: int = 10, sort_order=None
):
    """Helper function that mimics the actual search_cell_lines tool."""
    # Parse fields if provided
    field_enums = None
    if fields:
        try:
            field_enums = [CellosaurusField(field) for field in fields]
        except ValueError as e:
            return {"error": f"Invalid field specified: {e}"}

    request = SearchRequest(
        query=query,
        fields=field_enums,
        start=start,
        rows=min(rows, 1000),
        sort=sort_order,
    )

    try:
        return await client.search_cell_lines(request)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Search failed: {str(e)}"}


async def _get_cell_line_info_helper(accession: str, fields=None):
    """Helper function that mimics the actual get_cell_line_info tool."""
    field_enums = None
    if fields:
        try:
            field_enums = [CellosaurusField(field) for field in fields]
        except ValueError as e:
            return {"error": f"Invalid field specified: {e}"}

    request = CellLineRequest(
        accession=accession,
        fields=field_enums,
    )

    try:
        return await client.get_cell_line(request)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Failed to get cell line info: {str(e)}"}


def _list_available_fields_helper():
    """Helper function that mimics the actual list_available_fields tool."""
    return {
        # Basic identifiers
        "id": "Recommended name of the cell line",
        "sy": "List of synonyms",
        "idsy": "Recommended name with all synonyms",
        "ac": "Primary accession (unique identifier)",
        "acas": "Primary and secondary accessions",
        # Cross-references and publications
        "dr": "Cross-references to external resources",
        "ref": "Publication references",
        "rx": "Publication cross-reference",
        "ra": "Publication authors",
        "rt": "Publication title",
        "rl": "Publication citation elements",
        "ww": "Web page related to the cell line",
        # Biological characteristics
        "genome-ancestry": "Ethnic ancestry based on genome analysis",
        "hla": "HLA typing information",
        "sequence-variation": "Important sequence variations",
        "cell-type": "Cell type from which the cell line is derived",
        "derived-from-site": "Body part (tissue/organ) the cell line is derived from",
        "karyotype": "Chromosomal information",
        "str": "Short tandem repeat profile",
        # Disease and organism info
        "di": "Diseases suffered by the donor",
        "ox": "Species of origin with NCBI taxon identifier",
        "sx": "Sex of the individual",
        "ag": "Age at sampling time",
        # Relationships
        "hi": "Parent cell line",
        "ch": "Child cell lines",
        "oi": "Sister cell lines from same individual",
        "ca": "Category (e.g., cancer cell line, hybridoma)",
        # Comments and metadata
        "cc": "Various structured comments",
        "dt": "Creation/modification dates and version",
    }


async def _find_cell_lines_by_disease_helper(disease: str, species: str = "human", fields=None, limit: int = 10):
    """Helper function that mimics the actual find_cell_lines_by_disease tool."""
    query_parts = [f"di:{disease}"]
    if species:
        query_parts.append(f"ox:{species}")

    query = " ".join(query_parts)

    return await _search_cell_lines_helper(
        query=query,
        fields=fields or ["id", "ac", "di", "ox", "derived-from-site"],
        rows=limit,
    )


async def _find_cell_lines_by_tissue_helper(tissue: str, species: str = "human", fields=None, limit: int = 10):
    """Helper function that mimics the actual find_cell_lines_by_tissue tool."""
    query_parts = [f"derived-from-site:{tissue}"]
    if species:
        query_parts.append(f"ox:{species}")

    query = " ".join(query_parts)

    return await _search_cell_lines_helper(
        query=query,
        fields=fields or ["id", "ac", "derived-from-site", "ox", "cell-type"],
        rows=limit,
    )


def test_package_has_version():
    """Test that the package has a version."""
    assert cellosaurus_mcp.__version__ is not None


class TestCellosaurusModels:
    """Test Pydantic models for API requests."""

    def test_search_request_defaults(self):
        """Test SearchRequest with default values."""
        request = SearchRequest()
        assert request.query == "id:HeLa"  # This is the default value
        assert request.format == Format.JSON
        assert request.start == 0
        assert request.rows == 1000  # This is the default value

    def test_search_request_with_fields(self):
        """Test SearchRequest with specific fields."""
        request = SearchRequest(query="id:HeLa", fields=[CellosaurusField.ID, CellosaurusField.AC], rows=20)
        assert request.query == "id:HeLa"
        assert request.fields is not None
        assert len(request.fields) == 2
        assert request.rows == 20

    def test_cell_line_request(self):
        """Test CellLineRequest model."""
        request = CellLineRequest(accession="CVCL_0030")
        assert request.accession == "CVCL_0030"
        assert request.format == Format.JSON


class TestCellosaurusClient:
    """Test the HTTP client functionality."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return CellosaurusClient(timeout=10.0)

    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.timeout == 10.0
        assert client.BASE_URL == "https://api.cellosaurus.org"

    def test_build_params_search_request(self, client):
        """Test parameter building for search requests."""
        request = SearchRequest(query="id:HeLa", fields=[CellosaurusField.ID, CellosaurusField.AC], start=10, rows=20)
        params = client._build_params(request)

        assert params["q"] == "id:HeLa"
        assert params["fields"] == "id,ac"
        assert params["start"] == 10
        assert params["rows"] == 20

    def test_build_params_cell_line_request(self, client):
        """Test parameter building for cell line requests."""
        request = CellLineRequest(accession="CVCL_0030", fields=[CellosaurusField.ID, CellosaurusField.STR])
        params = client._build_params(request)

        assert params["fields"] == "id,str"
        assert "format" not in params  # JSON is default


class TestCellosaurusTools:
    """Test the MCP tools."""

    def test_list_available_fields_functionality(self):
        """Test that list_available_fields returns expected fields."""
        fields = _list_available_fields_helper()
        # Check that key fields are present
        assert "id" in fields
        assert "ac" in fields
        assert "ox" in fields
        assert "di" in fields
        assert "str" in fields

        # Check that descriptions are strings
        assert isinstance(fields["id"], str)
        assert len(fields["id"]) > 0

    @pytest.mark.asyncio
    async def test_search_cell_lines_basic(self):
        """Test basic cell line search."""
        # Mock the client response
        mock_response = {
            "results": [{"id": "HeLa", "ac": "CVCL_0030"}, {"id": "HeLa-S3", "ac": "CVCL_0031"}],
            "total_found": 2,
            "start": 0,
            "rows": 2,
        }

        with patch(
            "cellosaurus_mcp.client.client.search_cell_lines", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await _search_cell_lines_helper(query="id:HeLa", rows=5)

            assert "results" in result
            assert len(result["results"]) == 2
            assert result["results"][0]["id"] == "HeLa"

    @pytest.mark.asyncio
    async def test_search_cell_lines_invalid_field(self):
        """Test search with invalid field returns error."""
        result = await _search_cell_lines_helper(query="id:HeLa", fields=["invalid_field"])

        assert "error" in result
        assert "Invalid field" in result["error"]

    @pytest.mark.asyncio
    async def test_get_cell_line_info_basic(self):
        """Test getting cell line info by accession."""
        mock_response = {"id": "HeLa", "ac": "CVCL_0030", "ox": "Homo sapiens", "di": "Cervix adenocarcinoma"}

        with patch("cellosaurus_mcp.client.client.get_cell_line", new_callable=AsyncMock, return_value=mock_response):
            result = await _get_cell_line_info_helper(accession="CVCL_0030")

            assert result["id"] == "HeLa"
            assert result["ac"] == "CVCL_0030"

    @pytest.mark.asyncio
    async def test_find_cell_lines_by_disease(self):
        """Test finding cell lines by disease."""
        mock_response = {"results": [{"id": "Huh-7", "ac": "CVCL_0336", "di": "Hepatoblastoma"}], "total_found": 1}

        with patch(
            "cellosaurus_mcp.client.client.search_cell_lines", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await _find_cell_lines_by_disease_helper(disease="hepatoblastoma", species="human", limit=5)

            assert "results" in result
            assert len(result["results"]) == 1
            assert result["results"][0]["id"] == "Huh-7"

    @pytest.mark.asyncio
    async def test_find_cell_lines_by_tissue(self):
        """Test finding cell lines by tissue."""
        mock_response = {
            "results": [{"id": "Huh-7", "ac": "CVCL_0336", "derived-from-site": "liver"}],
            "total_found": 1,
        }

        with patch(
            "cellosaurus_mcp.client.client.search_cell_lines", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await _find_cell_lines_by_tissue_helper(tissue="liver", species="human", limit=5)

            assert "results" in result
            assert len(result["results"]) == 1
            assert "liver" in result["results"][0]["derived-from-site"]
