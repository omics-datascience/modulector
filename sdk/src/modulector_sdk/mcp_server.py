"""MCP server exposing Modulector SDK services to LLM clients."""

from __future__ import annotations

import argparse
from typing import Any, Final, Literal, TypeVar, cast

from mcp.server.fastmcp import FastMCP

from . import services
from .utils import PaginatedResponse

T = TypeVar("T")
Transport = Literal["stdio", "sse", "streamable-http"]

SERVER_INSTRUCTIONS: Final[str] = (
    "Use Modulector to help researchers inspect human miRNA target "
    "interactions, miRNA aliases, disease and drug associations, and "
    "Illumina methylation site annotations. Prefer finder tools when the "
    "user gives partial or uncertain identifiers, then use the detail or "
    "paginated tools with explicit identifiers. The returned data comes from "
    "the configured Modulector API deployment."
)

mcp = FastMCP(
    name="modulector",
    instructions=SERVER_INSTRUCTIONS,
    website_url=services.MODULECTOR_API_BASE_URL,
)


@mcp.resource(
    "modulector://about",
    title="About Modulector",
    description="Overview of the Modulector data exposed by this MCP server.",
    mime_type="text/markdown",
)
def about_modulector() -> str:
    """Return a concise overview of this MCP server.

    :return: Markdown overview for LLM context.
    """

    return (
        "# Modulector\n\n"
        "Modulector provides programmatic access to curated human miRNA target "
        "interactions, miRNA aliases, miRNA-disease associations, "
        "miRNA-drug associations, and Illumina Infinium MethylationEPIC 2.0 "
        "site annotations.\n\n"
        f"Default API base URL: `{services.MODULECTOR_API_BASE_URL}`\n\n"
        "Use the finder tools for partial identifiers, then query detail or "
        "paginated tools with exact miRNA, gene, disease, drug, or methylation "
        "site filters."
    )


@mcp.prompt(
    name="modulector_research_plan",
    title="Modulector Research Plan",
    description="Guide an LLM through a focused Modulector research lookup.",
)
def modulector_research_plan(research_question: str) -> str:
    """Return a prompt for planning a Modulector lookup.

    :param research_question: Research question to investigate.
    :return: Prompt text that guides tool selection and result synthesis.
    """

    return (
        "Plan a Modulector lookup for this research question:\n\n"
        f"{research_question}\n\n"
        "First identify whether the task involves miRNA identifiers, gene "
        "symbols, diseases, drugs, or methylation sites. Use finder or alias "
        "tools to normalize uncertain identifiers. Then retrieve the smallest "
        "useful page of records, include PubMed links only when needed, and "
        "summarize the evidence with clear caveats about database scope."
    )


@mcp.tool()
def get_mirna_target_interactions(
    mirna: str | None = None,
    gene: str | None = None,
    score: float | None = None,
    include_pubmeds: bool | None = None,
    ordering: str | None = None,
    search: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return miRNA-gene target interactions from Modulector.

    :param mirna: miRNA accession ID or miRBase mature name.
    :param gene: Gene symbol.
    :param score: Minimum MirDIP score between 0 and 1.
    :param include_pubmeds: Whether to include PubMed URLs for interactions.
    :param ordering: Comma-separated ordering fields, such as ``-score,gene``.
    :param search: Search term for supported server-side fields.
    :param page: Page number to request.
    :param page_size: Number of records to request.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Paginated interaction records.
    """

    return _page_to_dict(
        services.get_mirna_target_interactions(
            base_url=_base_url(base_url),
            mirna=mirna,
            gene=gene,
            score=score,
            include_pubmeds=include_pubmeds,
            ordering=ordering,
            search=search,
            page=page,
            page_size=page_size,
            timeout=timeout,
        )
    )


@mcp.tool()
def get_mirna_details(
    mirna: str,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return sequence, aliases, accession, and source links for one miRNA.

    :param mirna: miRNA identifier, such as a mature miRNA ID or accession ID.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: miRNA detail record.
    """

    return services.get_mirna_details(
        mirna,
        base_url=_base_url(base_url),
        timeout=timeout,
    )


@mcp.tool()
def get_mirna_aliases(
    mature_mirna: str | None = None,
    mirbase_accession_id: str | None = None,
    previous_mature_mirna: str | None = None,
    search: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return miRBase accession and mature miRNA alias records.

    :param mature_mirna: Exact mature miRNA filter.
    :param mirbase_accession_id: Exact miRBase accession ID filter.
    :param previous_mature_mirna: Exact previous mature miRNA filter.
    :param search: Search across mature IDs, previous IDs, and accessions.
    :param ordering: Comma-separated ordering fields.
    :param page: Page number to request.
    :param page_size: Number of records to request.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Paginated miRNA alias records.
    """

    return _page_to_dict(
        services.get_mirna_aliases(
            base_url=_base_url(base_url),
            mature_mirna=mature_mirna,
            mirbase_accession_id=mirbase_accession_id,
            previous_mature_mirna=previous_mature_mirna,
            search=search,
            ordering=ordering,
            page=page,
            page_size=page_size,
            timeout=timeout,
        )
    )


@mcp.tool()
def find_mirna_codes(
    query: str,
    limit: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> list[str]:
    """Return miRNA identifiers matching a partial search string.

    :param query: miRNA search string.
    :param limit: Maximum number of identifiers to return.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Matching miRNA IDs or accession IDs.
    """

    return services.find_mirna_codes(
        query,
        base_url=_base_url(base_url),
        limit=limit,
        timeout=timeout,
    )


@mcp.tool()
def get_mirna_codes(
    mirna_codes: list[str],
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, str | None]:
    """Resolve miRNA identifiers to approved miRBase accessions.

    :param mirna_codes: miRNA identifiers to resolve.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Mapping from requested identifiers to accession IDs or null.
    """

    return services.get_mirna_codes(
        mirna_codes,
        base_url=_base_url(base_url),
        timeout=timeout,
    )


@mcp.tool()
def find_methylation_sites(
    query: str,
    limit: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> list[str]:
    """Return methylation site names matching a partial search string.

    :param query: Methylation site search string.
    :param limit: Maximum number of site names to return.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Matching methylation site names.
    """

    return services.find_methylation_sites(
        query,
        base_url=_base_url(base_url),
        limit=limit,
        timeout=timeout,
    )


@mcp.tool()
def get_methylation_sites(
    methylation_sites: list[str],
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, list[str]]:
    """Resolve methylation identifiers to EPIC 2.0 site names.

    :param methylation_sites: Illumina methylation site names or identifiers.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Mapping from requested identifiers to current EPIC 2.0 names.
    """

    return services.get_methylation_sites(
        methylation_sites,
        base_url=_base_url(base_url),
        timeout=timeout,
    )


@mcp.tool()
def get_methylation_site_genes(
    methylation_sites: list[str],
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, list[str]]:
    """Return genes associated with methylation site identifiers.

    :param methylation_sites: Illumina methylation site names or identifiers.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Mapping from requested site identifiers to associated genes.
    """

    return services.get_methylation_site_genes(
        methylation_sites,
        base_url=_base_url(base_url),
        timeout=timeout,
    )


@mcp.tool()
def get_methylation_details(
    methylation_site: str,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return detailed annotations for one methylation site.

    :param methylation_site: Methylation site name from EPIC 2.0.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Methylation site detail record.
    """

    return services.get_methylation_details(
        methylation_site,
        base_url=_base_url(base_url),
        timeout=timeout,
    )


@mcp.tool()
def get_diseases(
    mirna: str | None = None,
    search: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return miRNA and human disease association records.

    :param mirna: miRNA code or accession ID filter.
    :param search: Case-insensitive disease search term.
    :param ordering: Comma-separated ordering fields.
    :param page: Page number to request.
    :param page_size: Number of records to request.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Paginated disease association records.
    """

    return _page_to_dict(
        services.get_diseases(
            base_url=_base_url(base_url),
            mirna=mirna,
            search=search,
            ordering=ordering,
            page=page,
            page_size=page_size,
            timeout=timeout,
        )
    )


@mcp.tool()
def get_drugs(
    mirna: str | None = None,
    fda_approved: bool | None = None,
    search: str | None = None,
    ordering: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    base_url: str | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Return drug or small molecule records affecting miRNA expression.

    :param mirna: miRNA code or accession ID filter.
    :param fda_approved: Optional FDA approval filter.
    :param search: Search term for condition, molecule, or expression fields.
    :param ordering: Comma-separated ordering fields.
    :param page: Page number to request.
    :param page_size: Number of records to request.
    :param base_url: Optional Modulector API deployment URL.
    :param timeout: Request timeout in seconds.
    :return: Paginated drug association records.
    """

    return _page_to_dict(
        services.get_drugs(
            base_url=_base_url(base_url),
            mirna=mirna,
            fda_approved=fda_approved,
            search=search,
            ordering=ordering,
            page=page,
            page_size=page_size,
            timeout=timeout,
        )
    )


def main() -> None:
    """Run the Modulector MCP server.

    :return: Nothing.
    """

    args = _parse_args()
    transport = cast(Transport, args.transport)
    if transport != "stdio":
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.settings.json_response = args.json_response
    mcp.run(transport=transport)


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the MCP server.

    :return: Parsed command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description="Run the Modulector MCP server.",
    )
    parser.add_argument(
        "--transport",
        choices=("stdio", "sse", "streamable-http"),
        default="stdio",
        help="MCP transport to use. Defaults to stdio.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP transports. Defaults to 127.0.0.1.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transports. Defaults to 8000.",
    )
    parser.add_argument(
        "--json-response",
        action="store_true",
        help="Use JSON responses for Streamable HTTP instead of SSE streams.",
    )
    return parser.parse_args()


def _base_url(base_url: str | None) -> str:
    """Return the requested or default Modulector API base URL.

    :param base_url: Optional Modulector API deployment URL.
    :return: API base URL.
    """

    return base_url or services.MODULECTOR_API_BASE_URL


def _page_to_dict(page: PaginatedResponse[T]) -> dict[str, Any]:
    """Convert a paginated SDK response into a JSON-serializable mapping.

    :param page: SDK paginated response.
    :return: Mapping with pagination metadata and results.
    """

    return {
        "count": page.count,
        "next": page.next,
        "previous": page.previous,
        "results": page.results,
    }


if __name__ == "__main__":
    main()
