"""HTTP client for Cellosaurus API."""

from __future__ import annotations

from typing import Any

import httpx

from .models import CellLineRequest, Format, ReleaseInfoRequest, SearchRequest


class CellosaurusClient:
    """HTTP client for the Cellosaurus API."""

    BASE_URL = "https://api.cellosaurus.org"
    TIMEOUT = 30.0

    def __init__(self, timeout: float = TIMEOUT) -> None:
        """Initialize the client."""
        self.timeout = timeout

    def _build_params(self, request: SearchRequest | CellLineRequest | ReleaseInfoRequest) -> dict[str, Any]:
        """Build query parameters from request model."""
        params = {}

        if hasattr(request, "query") and request.query:
            params["q"] = request.query

        if hasattr(request, "start") and request.start is not None:
            params["start"] = request.start

        if hasattr(request, "rows") and request.rows is not None:
            params["rows"] = request.rows

        if hasattr(request, "sort") and request.sort:
            params["sort"] = request.sort

        if request.format != Format.JSON:
            params["format"] = request.format.value

        if hasattr(request, "fields") and request.fields:
            params["fields"] = ",".join(field.value for field in request.fields)

        return params

    async def get_release_info(self, request: ReleaseInfoRequest) -> dict[str, Any]:
        """Get Cellosaurus release information."""
        params = self._build_params(request)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}/release-info", params=params)
            response.raise_for_status()

            if request.format == Format.JSON:
                return response.json()
            return {"data": response.text, "format": request.format.value}

    async def get_cell_line(self, request: CellLineRequest) -> dict[str, Any]:
        """Get information about a specific cell line by accession."""
        params = self._build_params(request)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}/cell-line/{request.accession}", params=params)
            response.raise_for_status()

            if request.format == Format.JSON:
                return response.json()
            return {"data": response.text, "format": request.format.value}

    async def search_cell_lines(self, request: SearchRequest) -> dict[str, Any]:
        """Search for cell lines."""
        params = self._build_params(request)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.BASE_URL}/search/cell-line", params=params)
            response.raise_for_status()

            if request.format == Format.JSON:
                result = response.json()
                # Parse Solr-style response if needed
                if isinstance(result, dict) and "response" in result:
                    return {
                        "results": result["response"].get("docs", []),
                        "total_found": result["response"].get("numFound", 0),
                        "start": result["response"].get("start", 0),
                        "rows": len(result["response"].get("docs", [])),
                        "format": request.format.value,
                    }
                return result
            return {"data": response.text, "format": request.format.value}


# Global client instance
client = CellosaurusClient()
