"""Typed service functions for Modulector API endpoints."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any, Final, Literal, TypedDict, cast

import requests

from .utils import (
    Headers,
    PaginatedResponse,
    get_paginated_response,
    get_simple_response,
)

MODULECTOR_API_BASE_URL: Final[str] = os.getenv(
    "MODULECTOR_API_BASE_URL",
    "https://modulector.multiomix.org",
)
API_BASE_URL: Final[str] = MODULECTOR_API_BASE_URL
FINDER_LIMIT_MAX: Final[int] = 3000

Ordering = str | Sequence[str]
ScoreClass = Literal["V", "H", "M", "L"]


class SourceLink(TypedDict):
    """External source link returned by detail endpoints."""

    source: str
    """Name of the external database that contains related information."""

    url: str
    """URL to access the external database entry."""


class MirnaDetailsResponse(TypedDict):
    """Response returned by the miRNA details service."""

    aliases: list[str]
    """miRNA aliases, including previous IDs according to miRBase."""

    mirna_sequence: str | None
    """miRNA nucleotide sequence."""

    mirbase_accession_id: str
    """miRNA accession ID according to miRBase."""

    links: list[SourceLink]
    """External database links for the miRNA of interest."""


class MirnaAlias(TypedDict):
    """One miRBase accession to mature miRNA alias record."""

    mirbase_accession_id: str
    """miRBase accession ID for the miRNA."""

    mature_mirna: str
    """Mature miRNA ID in the miRBase database."""

    previous_mature_mirna: str | None
    """Previous mature miRNA identifier associated with the same accession ID."""


class MirnaTargetInteraction(TypedDict):
    """One miRNA target interaction record."""

    id: int
    """Record identifier in MirDIP."""

    mirna: str
    """Standardized miRNA ID used by the interaction record."""

    mirna_aliases: list[str]
    """Aliases and identifiers used to resolve the searched miRNA."""

    gene: str
    """Target gene symbol."""

    gene_aliases: list[str]
    """Aliases and symbols associated with the searched gene."""

    score: str
    """MirDIP interaction score, with values between 0 and 1."""

    source_name: str
    """Database from which the interaction was extracted."""

    pubmeds: list[str]
    """PubMed URLs for the miRNA-gene interaction."""

    sources: list[str]
    """Source database names used to calculate the MirDIP interaction score."""

    score_class: ScoreClass | None
    """MirDIP score class for the interaction."""


class MirnaDisease(TypedDict):
    """One miRNA disease association record."""

    id: int
    """Internal ID of the record in the HMDD database."""

    category: str
    """HMDD category code assigned to classify the disease association."""

    disease: str
    """Name of the disease associated with the miRNA."""

    pubmed: str
    """PubMed URL for the scientific article supporting the association."""

    description: str
    """Short description of why the miRNA is related to the disease."""


class MirnaDrug(TypedDict):
    """One miRNA drug association record."""

    id: int
    """Internal ID of the record in the SM2miR database."""

    small_molecule: str
    """Small molecule or drug name."""

    fda_approved: bool
    """Whether the small molecule or drug is FDA approved."""

    detection_method: str
    """Experimental method used to detect the miRNA expression effect."""

    condition: str
    """Tissue or condition used for detection."""

    pubmed: str
    """PubMed URL for the scientific article supporting the relationship."""

    reference: str
    """Title of the scientific article supporting the relationship."""

    expression_pattern: str
    """Expression pattern of the miRNA in the drug relationship."""

    support: str
    """Supporting text for the drug-miRNA relationship."""


class UcscCpgIsland(TypedDict):
    """UCSC CpG island relation for a methylation site."""

    cpg_island: str
    """Chromosomal coordinates of the CpG island."""

    relation: str
    """Relation of the methylation site to the CpG island."""


class MethylationDetailsResponse(TypedDict):
    """Response returned by the methylation site details service."""

    name: str
    """Methylation site name according to the Illumina Infinium MethylationEPIC
    2.0 array.
    """

    aliases: list[str]
    """Other names for the same methylation site on Illumina arrays."""

    chromosome_position: str
    """Chromosome, position, and strand where the methylation site is located."""

    ucsc_cpg_islands: list[UcscCpgIsland]
    """CpG islands related to the methylation site according to UCSC."""

    genes: dict[str, list[str]]
    """Genes related to the methylation site and their affected regions."""


class SubscribePubmedsResponse(TypedDict):
    """Response returned after creating a PubMed news subscription."""

    token: str
    """Subscription token."""


def get_mirna_target_interactions(
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    mirna: str | None = None,
    gene: str | None = None,
    score: float | None = None,
    include_pubmeds: bool | None = None,
    ordering: Ordering | None = None,
    search: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PaginatedResponse[MirnaTargetInteraction]:
    """Return miRNA-gene target interactions.

    :param base_url: Base URL of the Modulector API.
    :param mirna: miRNA accession ID or miRBase name.
    :param gene: Gene symbol.
    :param score: Minimum mirDIP interaction score. Valid values are between
        ``0`` and ``1``.
    :param include_pubmeds: Whether PubMed links should be included.
    :param ordering: Ordering field or comma-separated fields. Prefix a field
        with ``-`` for descending order.
    :param search: Search term for supported server-side search fields.
    :param page: Page number to request.
    :param page_size: Number of records per page.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :raises ValueError: If neither ``mirna`` nor ``gene`` is provided, or if
        ``score`` is outside the accepted range.
    :return: Paginated miRNA target interaction records.
    """

    if mirna is None and gene is None:
        raise ValueError("mirna or gene is required")
    if score is not None and not 0 <= score <= 1:
        raise ValueError("score must be between 0 and 1")

    params = _request_params(
        mirna=mirna,
        gene=gene,
        score=score,
        include_pubmeds=_bool_param(include_pubmeds),
        ordering=_format_ordering(ordering),
        search=search,
    )
    response = get_paginated_response(
        _build_url(base_url, "mirna-target-interactions"),
        params=params,
        page=page,
        page_size=page_size,
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(PaginatedResponse[MirnaTargetInteraction], response)


def get_mirna_details(
    mirna: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> MirnaDetailsResponse:
    """Return details for one miRNA.

    :param mirna: miRNA identifier, such as a miRNA code or accession ID.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: miRNA aliases, sequence, accession ID, and source links.
    """

    payload = get_simple_response(
        _build_url(base_url, "mirna"),
        params={"mirna": mirna},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(MirnaDetailsResponse, payload)


def get_mirna_aliases(
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    mature_mirna: str | None = None,
    mirbase_accession_id: str | None = None,
    previous_mature_mirna: str | None = None,
    search: str | None = None,
    ordering: Ordering | None = None,
    page: int | None = None,
    page_size: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PaginatedResponse[MirnaAlias]:
    """Return miRNA accession and mature ID alias records.

    :param base_url: Base URL of the Modulector API.
    :param mature_mirna: Exact mature miRNA filter.
    :param mirbase_accession_id: Exact miRBase accession ID filter.
    :param previous_mature_mirna: Exact previous mature miRNA filter.
    :param search: Case-insensitive search across identifier fields.
    :param ordering: Ordering field or comma-separated fields. Prefix a field
        with ``-`` for descending order.
    :param page: Page number to request.
    :param page_size: Number of records per page.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Paginated miRNA alias records.
    """

    params = _request_params(
        mature_mirna=mature_mirna,
        mirbase_accession_id=mirbase_accession_id,
        previous_mature_mirna=previous_mature_mirna,
        search=search,
        ordering=_format_ordering(ordering),
    )
    response = get_paginated_response(
        _build_url(base_url, "mirna-aliases"),
        params=params,
        page=page,
        page_size=page_size,
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(PaginatedResponse[MirnaAlias], response)


def find_mirna_codes(
    query: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    limit: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[str]:
    """Return miRNA identifiers matching a search string.

    :param query: miRNA search string.
    :param base_url: Base URL of the Modulector API.
    :param limit: Maximum number of returned values. The API accepts values up
        to ``3000``.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :raises ValueError: If ``limit`` is less than ``1`` or greater than
        ``3000``.
    :return: Matching miRNA IDs or accession IDs.
    """

    _validate_limit(limit)
    payload = get_simple_response(
        _build_url(base_url, "mirna-codes-finder"),
        params=_request_params(query=query, limit=limit),
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(list[str], payload)


def get_mirna_codes(
    mirna_codes: Sequence[str],
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> dict[str, str | None]:
    """Return approved miRBase accessions for miRNA identifiers.

    :param mirna_codes: miRNA identifiers to resolve.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Mapping from each requested identifier to its accession ID, or
        ``None`` when no accession ID is found.
    """

    payload = get_simple_response(
        _build_url(base_url, "mirna-codes"),
        method="POST",
        json={"mirna_codes": list(mirna_codes)},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(dict[str, str | None], payload)


def find_methylation_sites(
    query: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    limit: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[str]:
    """Return methylation site names matching a search string.

    :param query: Methylation site search string.
    :param base_url: Base URL of the Modulector API.
    :param limit: Maximum number of returned values. The API accepts values up
        to ``3000``.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :raises ValueError: If ``limit`` is less than ``1`` or greater than
        ``3000``.
    :return: Matching methylation site names.
    """

    _validate_limit(limit)
    payload = get_simple_response(
        _build_url(base_url, "methylation-sites-finder"),
        params=_request_params(query=query, limit=limit),
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(list[str], payload)


def get_methylation_sites(
    methylation_sites: Sequence[str],
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> dict[str, list[str]]:
    """Return current EPIC 2.0 names for methylation site identifiers.

    :param methylation_sites: Illumina methylation site names or identifiers.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Mapping from each requested identifier to matching EPIC 2.0 site
        names.
    """

    payload = get_simple_response(
        _build_url(base_url, "methylation-sites"),
        method="POST",
        json={"methylation_sites": list(methylation_sites)},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(dict[str, list[str]], payload)


def get_methylation_site_genes(
    methylation_sites: Sequence[str],
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> dict[str, list[str]]:
    """Return genes associated with methylation site identifiers.

    :param methylation_sites: Illumina methylation site names or identifiers.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Mapping from each requested identifier to associated genes.
    """

    payload = get_simple_response(
        _build_url(base_url, "methylation-sites-genes"),
        method="POST",
        json={"methylation_sites": list(methylation_sites)},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(dict[str, list[str]], payload)


def get_methylation_details(
    methylation_site: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> MethylationDetailsResponse:
    """Return details for one methylation site.

    :param methylation_site: Methylation site name from the Infinium
        MethylationEPIC 2.0 array.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Methylation site details, aliases, CpG island relations, and genes.
    """

    payload = get_simple_response(
        _build_url(base_url, "methylation"),
        params={"methylation_site": methylation_site},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(MethylationDetailsResponse, payload)


def get_diseases(
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    mirna: str | None = None,
    search: str | None = None,
    ordering: Ordering | None = None,
    page: int | None = None,
    page_size: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PaginatedResponse[MirnaDisease]:
    """Return miRNA and human disease association records.

    :param base_url: Base URL of the Modulector API.
    :param mirna: miRNA code or accession ID. If omitted, all records are
        returned page by page.
    :param search: Case-insensitive search term for disease names.
    :param ordering: Ordering field or comma-separated fields. Prefix a field
        with ``-`` for descending order.
    :param page: Page number to request.
    :param page_size: Number of records per page.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Paginated miRNA disease association records.
    """

    params = _request_params(
        mirna=mirna,
        search=search,
        ordering=_format_ordering(ordering),
    )
    response = get_paginated_response(
        _build_url(base_url, "diseases"),
        params=params,
        page=page,
        page_size=page_size,
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(PaginatedResponse[MirnaDisease], response)


def get_drugs(
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    mirna: str | None = None,
    fda_approved: bool | None = None,
    search: str | None = None,
    ordering: Ordering | None = None,
    page: int | None = None,
    page_size: int | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PaginatedResponse[MirnaDrug]:
    """Return drug or small molecule records affecting miRNA expression.

    :param base_url: Base URL of the Modulector API.
    :param mirna: miRNA code or accession ID. If omitted, all records are
        returned page by page.
    :param fda_approved: Optional FDA approval filter.
    :param search: Case-insensitive search term for condition, small molecule,
        and expression pattern fields.
    :param ordering: Ordering field or comma-separated fields. Prefix a field
        with ``-`` for descending order.
    :param page: Page number to request.
    :param page_size: Number of records per page.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Paginated miRNA drug association records.
    """

    params = _request_params(
        mirna=mirna,
        fda_approved=_bool_param(fda_approved),
        search=search,
        ordering=_format_ordering(ordering),
    )
    response = get_paginated_response(
        _build_url(base_url, "drugs"),
        params=params,
        page=page,
        page_size=page_size,
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(PaginatedResponse[MirnaDrug], response)


def subscribe_pubmeds(
    mirna: str,
    email: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    gene: str | None = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> SubscribePubmedsResponse:
    """Subscribe an email address to PubMed news for a miRNA.

    :param mirna: miRNA code or accession ID.
    :param email: Email address to subscribe.
    :param base_url: Base URL of the Modulector API.
    :param gene: Optional gene symbol filter for the subscription.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: Subscription token response.
    """

    payload = get_simple_response(
        _build_url(base_url, "subscribe-pubmeds"),
        params=_request_params(mirna=mirna, email=email, gene=gene),
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(SubscribePubmedsResponse, payload)


def unsubscribe_pubmeds(
    token: str,
    *,
    base_url: str = MODULECTOR_API_BASE_URL,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> str:
    """Unsubscribe from PubMed news.

    :param token: Subscription token returned by ``subscribe_pubmeds``.
    :param base_url: Base URL of the Modulector API.
    :param headers: Optional HTTP headers.
    :param timeout: Request timeout in seconds.
    :param session: Optional ``requests.Session`` to use for the request.
    :return: API confirmation message.
    """

    payload = get_simple_response(
        _build_url(base_url, "unsubscribe-pubmeds"),
        params={"token": token},
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return cast(str, payload)


def _build_url(base_url: str, endpoint: str) -> str:
    """Build an absolute endpoint URL with a trailing slash.

    :param base_url: Base URL of the Modulector API.
    :param endpoint: Endpoint path with or without leading or trailing slashes.
    :return: Absolute URL for the endpoint.
    """

    return f"{base_url.rstrip('/')}/{endpoint.strip('/')}/"


def _request_params(**params: Any) -> dict[str, Any]:
    """Return request parameters without ``None`` values.

    :param params: Query parameters keyed by API parameter name.
    :return: A dictionary containing only parameters with non-``None`` values.
    """

    return {key: value for key, value in params.items() if value is not None}


def _bool_param(value: bool | None) -> str | None:
    """Convert an optional boolean to the API's lowercase string form.

    :param value: Boolean value to convert.
    :return: ``"true"``, ``"false"``, or ``None``.
    """

    if value is None:
        return None
    return "true" if value else "false"


def _format_ordering(ordering: Ordering | None) -> str | None:
    """Format an ordering value for Django REST Framework query parameters.

    :param ordering: A comma-separated ordering string or a sequence of ordering
        fields.
    :return: A comma-separated ordering string, or ``None``.
    """

    if ordering is None:
        return None
    if isinstance(ordering, str):
        return ordering

    ordering_fields = [field for field in ordering if field]
    if not ordering_fields:
        return None
    return ",".join(ordering_fields)


def _validate_limit(limit: int | None) -> None:
    """Validate finder service limit parameters.

    :param limit: Limit value to validate.
    :raises ValueError: If ``limit`` is outside the API's accepted range.
    :return: ``None``.
    """

    if limit is not None and not 1 <= limit <= FINDER_LIMIT_MAX:
        raise ValueError(f"limit must be between 1 and {FINDER_LIMIT_MAX}")


__all__ = [
    "API_BASE_URL",
    "MODULECTOR_API_BASE_URL",
    "MethylationDetailsResponse",
    "MirnaAlias",
    "MirnaDetailsResponse",
    "MirnaDisease",
    "MirnaDrug",
    "MirnaTargetInteraction",
    "SourceLink",
    "SubscribePubmedsResponse",
    "UcscCpgIsland",
    "find_methylation_sites",
    "find_mirna_codes",
    "get_diseases",
    "get_drugs",
    "get_methylation_details",
    "get_methylation_site_genes",
    "get_methylation_sites",
    "get_mirna_aliases",
    "get_mirna_codes",
    "get_mirna_details",
    "get_mirna_target_interactions",
    "subscribe_pubmeds",
    "unsubscribe_pubmeds",
]
