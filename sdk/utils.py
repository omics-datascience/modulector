"""Utilities for calling Modulector API endpoints.

The public API returns either a plain JSON payload or a paginated payload with
``count``, ``next``, ``previous``, and ``results`` fields.
"""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from typing import Any

import requests

JSON = dict[str, Any] | list[Any] | str | int | float | bool | None
Params = Mapping[str, Any] | None
Headers = Mapping[str, str] | None


@dataclass(frozen=True)
class PaginatedResponse:
    """Representation of a Modulector paginated response."""

    count: int
    next: str | None
    previous: str | None
    results: list[Any]


def request_url(
    url: str,
    *,
    method: str = "GET",
    params: Params = None,
    json: Any = None,
    data: Any = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> JSON:
    """Make an HTTP request and return the decoded JSON response.

    HTTP errors are raised with ``requests.Response.raise_for_status()``.
    JSON decoding errors are propagated from ``requests``.
    """

    client = session or requests
    response = client.request(
        method.upper(),
        url,
        params=params,
        json=json,
        data=data,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def get_simple_response(
    url: str,
    *,
    method: str = "GET",
    params: Params = None,
    json: Any = None,
    data: Any = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> JSON:
    """Return a non-paginated JSON response from an API endpoint."""

    return request_url(
        url,
        method=method,
        params=params,
        json=json,
        data=data,
        headers=headers,
        timeout=timeout,
        session=session,
    )


def get_paginated_response(
    url: str,
    *,
    method: str = "GET",
    params: Params = None,
    page: int | None = None,
    page_size: int | None = None,
    json: Any = None,
    data: Any = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> PaginatedResponse:
    """Return one page from an endpoint using Modulector pagination."""

    request_params = _with_pagination_params(params, page=page, page_size=page_size)
    payload = request_url(
        url,
        method=method,
        params=request_params,
        json=json,
        data=data,
        headers=headers,
        timeout=timeout,
        session=session,
    )
    return _parse_paginated_response(payload)


def iter_paginated_results(
    url: str,
    *,
    method: str = "GET",
    params: Params = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    json: Any = None,
    data: Any = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> Iterator[Any]:
    """Yield every result by following each paginated response's ``next`` URL."""

    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be greater than 0")

    next_url: str | None = url
    request_params = _with_pagination_params(params, page=None, page_size=page_size)
    pages_read = 0

    while next_url is not None:
        page = get_paginated_response(
            next_url,
            method=method,
            params=request_params,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            session=session,
        )
        yield from page.results

        pages_read += 1
        if max_pages is not None and pages_read >= max_pages:
            break

        next_url = page.next
        request_params = None


def get_all_paginated_results(
    url: str,
    *,
    method: str = "GET",
    params: Params = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    json: Any = None,
    data: Any = None,
    headers: Headers = None,
    timeout: float = 30.0,
    session: requests.Session | None = None,
) -> list[Any]:
    """Return all results from a paginated endpoint as a list."""

    return list(
        iter_paginated_results(
            url,
            method=method,
            params=params,
            page_size=page_size,
            max_pages=max_pages,
            json=json,
            data=data,
            headers=headers,
            timeout=timeout,
            session=session,
        )
    )


def _with_pagination_params(
    params: Params,
    *,
    page: int | None,
    page_size: int | None,
) -> dict[str, Any] | None:
    if page is not None and page < 1:
        raise ValueError("page must be greater than 0")
    if page_size is not None and not 1 <= page_size <= 1000:
        raise ValueError("page_size must be between 1 and 1000")

    if params is None and page is None and page_size is None:
        return None

    request_params = dict(params or {})
    if page is not None:
        request_params["page"] = page
    if page_size is not None:
        request_params["page_size"] = page_size
    return request_params


def _parse_paginated_response(payload: JSON) -> PaginatedResponse:
    if not isinstance(payload, Mapping):
        raise ValueError("paginated response must be a JSON object")

    missing_fields = {"count", "next", "previous", "results"} - payload.keys()
    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise ValueError(f"paginated response is missing fields: {missing}")

    results = payload["results"]
    if not isinstance(results, list):
        raise ValueError("paginated response field 'results' must be a list")

    next_url = payload["next"]
    previous_url = payload["previous"]
    if next_url is not None and not isinstance(next_url, str):
        raise ValueError("paginated response field 'next' must be a string or null")
    if previous_url is not None and not isinstance(previous_url, str):
        raise ValueError(
            "paginated response field 'previous' must be a string or null"
        )

    return PaginatedResponse(
        count=int(payload["count"]),
        next=next_url,
        previous=previous_url,
        results=results,
    )
