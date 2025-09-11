"""Cellosaurus MCP tools for cell line research."""

from __future__ import annotations

from typing import Any

from cellosaurus_mcp.client import client
from cellosaurus_mcp.mcp import mcp
from cellosaurus_mcp.models import CellLineRequest, CellosaurusField, ReleaseInfoRequest, SearchRequest


@mcp.tool
async def search_cell_lines(
    query: str = "id:HeLa",
    fields: list[str] | None = None,
    start: int = 0,
    rows: int = 10,
    sort_order: str | None = None,
) -> dict[str, Any]:
    """Search for cell lines in the Cellosaurus database.

    Use Solr search syntax to find cell lines by various criteria.

    Examples
    --------
    - Basic name search: "id:HeLa" or "sy:HeLa"
    - Species filter: "ox:human" or "ox:9606"
    - Disease filter: "di:cancer" or "di:hepatoblastoma"
    - Combined: "ox:human di:cancer ca:cancer"
    - Site filter: "derived-from-site:liver"

    Args:
        query: Search query using Solr syntax (default: "id:HeLa")
        fields: List of fields to return (e.g., ["id", "ac", "ox", "di"])
        start: Starting index for pagination (default: 0)
        rows: Number of results to return (default: 10, max: 1000)
        sort_order: Sort order (e.g., "group asc,derived-from-site desc")

    Returns
    -------
        Dictionary containing search results with cell line information
    """
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
        rows=min(rows, 1000),  # Cap at API limit
        sort=sort_order,
    )

    try:
        return await client.search_cell_lines(request)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool
async def get_cell_line_info(
    accession: str,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Get detailed information about a specific cell line by its accession number.

    Args:
        accession: Cell line accession number (e.g., "CVCL_0030" for HeLa)
        fields: List of specific fields to return (e.g., ["id", "ac", "str", "di"])

    Returns
    -------
        Dictionary containing detailed cell line information
    """
    # Parse fields if provided
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


@mcp.tool
async def get_release_info() -> dict[str, Any]:
    """Get information about the current Cellosaurus database release.

    Returns
    -------
        Dictionary containing release version, date, and statistics
    """
    request = ReleaseInfoRequest()

    try:
        return await client.get_release_info(request)
    except Exception as e:  # noqa: BLE001
        return {"error": f"Failed to get release info: {str(e)}"}


@mcp.tool
async def find_cell_lines_by_disease(
    disease: str,
    species: str = "human",
    fields: list[str] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Find cell lines derived from patients with a specific disease.

    Args:
        disease: Disease name or term (e.g., "hepatoblastoma", "cancer", "leukemia")
        species: Species filter (default: "human", can be "mouse", "rat", etc.)
        fields: Specific fields to return
        limit: Maximum number of results (default: 10)

    Returns
    -------
        Dictionary containing cell lines associated with the disease
    """
    # Build query for disease and species
    query_parts = [f"di:{disease}"]
    if species:
        query_parts.append(f"ox:{species}")

    query = " ".join(query_parts)

    return await search_cell_lines(
        query=query,
        fields=fields or ["id", "ac", "di", "ox", "derived-from-site"],
        rows=limit,
    )


@mcp.tool
async def find_cell_lines_by_tissue(
    tissue: str,
    species: str = "human",
    fields: list[str] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Find cell lines derived from a specific tissue or organ.

    Args:
        tissue: Tissue/organ name (e.g., "liver", "lung", "breast", "brain")
        species: Species filter (default: "human")
        fields: Specific fields to return
        limit: Maximum number of results (default: 10)

    Returns
    -------
        Dictionary containing cell lines from the specified tissue
    """
    # Build query for tissue and species
    query_parts = [f"derived-from-site:{tissue}"]
    if species:
        query_parts.append(f"ox:{species}")

    query = " ".join(query_parts)

    return await search_cell_lines(
        query=query,
        fields=fields or ["id", "ac", "derived-from-site", "ox", "cell-type"],
        rows=limit,
    )


@mcp.tool
def list_available_fields() -> dict[str, str]:
    """Get a list of all available fields that can be requested from the Cellosaurus API.

    Returns
    -------
        Dictionary mapping field names to their descriptions
    """
    field_descriptions = {
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

    return field_descriptions
