"""Pydantic models for Cellosaurus API."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Format(str, Enum):
    """Output format for API responses."""

    JSON = "json"
    XML = "xml"
    TXT = "txt"
    TSV = "tsv"


class CellosaurusField(str, Enum):
    """Available fields in Cellosaurus API responses."""

    # Basic identifiers and names
    ID = "id"  # Recommended name
    SY = "sy"  # Synonyms
    IDSY = "idsy"  # ID + synonyms
    AC = "ac"  # Primary accession
    ACAS = "acas"  # Primary + secondary accessions

    # Cross-references and publications
    DR = "dr"  # Cross-references
    REF = "ref"  # Publication references
    RX = "rx"  # Publication cross-reference
    RA = "ra"  # Publication authors
    RT = "rt"  # Publication title
    RL = "rl"  # Publication citation
    WW = "ww"  # Web page

    # Biological characteristics
    GENOME_ANCESTRY = "genome-ancestry"
    HLA = "hla"
    REGISTRATION = "registration"
    SEQUENCE_VARIATION = "sequence-variation"
    ANECDOTAL = "anecdotal"
    BIOTECHNOLOGY = "biotechnology"
    BREED = "breed"
    CAUTION = "caution"
    CELL_TYPE = "cell-type"
    CHARACTERISTICS = "characteristics"
    DONOR_INFO = "donor-info"
    DERIVED_FROM_SITE = "derived-from-site"
    DISCONTINUED = "discontinued"
    DOUBLING_TIME = "doubling-time"
    FROM = "from"
    GROUP = "group"
    KARYOTYPE = "karyotype"
    KNOCKOUT = "knockout"
    MSI = "msi"
    MISCELLANEOUS = "miscellaneous"
    MISSPELLING = "misspelling"
    MAB_ISOTYPE = "mab-isotype"
    MAB_TARGET = "mab-target"
    OMICS = "omics"
    PART_OF = "part-of"
    POPULATION = "population"
    PROBLEMATIC = "problematic"
    RESISTANCE = "resistance"
    SENESCENCE = "senescence"
    INTEGRATED = "integrated"
    TRANSFORMANT = "transformant"
    VIROLOGY = "virology"
    CC = "cc"  # Comments
    STR = "str"  # Short tandem repeat profile

    # Disease and organism info
    DI = "di"  # Diseases
    DIN = "din"  # Diseases (NCI Thesaurus)
    DIO = "dio"  # Diseases (ORDO)
    OX = "ox"  # Species
    SX = "sx"  # Sex
    AG = "ag"  # Age

    # Relationships
    OI = "oi"  # Sister cell lines
    HI = "hi"  # Parent cell line
    CH = "ch"  # Child cell lines
    CA = "ca"  # Category

    # Metadata
    DT = "dt"  # Creation/modification dates
    DTC = "dtc"  # Creation date
    DTU = "dtu"  # Last modification date
    DTV = "dtv"  # Version number


class SearchRequest(BaseModel):
    """Request model for cell line search."""

    query: str = Field(default="id:HeLa", description="Search query using Solr syntax")
    start: int = Field(default=0, description="Index of first result")
    rows: int = Field(default=1000, description="Number of results to return")
    format: Format = Field(default=Format.JSON, description="Response format")
    fields: list[CellosaurusField] | None = Field(default=None, description="Fields to return")
    sort: str | None = Field(default=None, description="Sort order (e.g., 'group asc,derived-from-site desc')")


class CellLineRequest(BaseModel):
    """Request model for getting a specific cell line."""

    accession: str = Field(description="Cell line accession number (e.g., 'CVCL_S151')")
    format: Format = Field(default=Format.JSON, description="Response format")
    fields: list[CellosaurusField] | None = Field(default=None, description="Fields to return")


class ReleaseInfoRequest(BaseModel):
    """Request model for release information."""

    format: Format = Field(default=Format.JSON, description="Response format")


class CellosaurusResponse(BaseModel):
    """Generic response model for Cellosaurus API."""

    data: dict[str, Any] = Field(description="Response data")
    format: Format = Field(description="Response format")


class SearchResponse(BaseModel):
    """Response model for search results."""

    results: list[dict[str, Any]] = Field(description="Search results")
    total_found: int = Field(description="Total number of results found")
    start: int = Field(description="Starting index")
    rows: int = Field(description="Number of rows returned")
