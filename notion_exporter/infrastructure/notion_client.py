"""HTTP adapter for Notion's public web endpoints."""

from __future__ import annotations

import re
from typing import Any

import requests


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
LOAD_PAGE_CHUNK_URL = "https://www.notion.so/api/v3/loadPageChunk"


class NotionClient:
    """Small requests-based client for public Notion pages."""

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = 30,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch_public_html(self, url: str) -> str:
        response = self.session.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "text/html"},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.text

    def load_page_chunk(
        self,
        block_id: str,
        referer: str,
        client_version: str | None,
        limit: int,
    ) -> dict[str, Any]:
        body = {
            "pageId": block_id,
            "limit": limit,
            "cursor": {"stack": []},
            "chunkNumber": 0,
            "verticalColumns": False,
        }
        response = self.session.post(
            LOAD_PAGE_CHUNK_URL,
            headers=self._json_headers(referer, client_version),
            json=body,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _json_headers(self, referer: str, client_version: str | None) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.notion.so",
            "Referer": referer,
            "User-Agent": DEFAULT_USER_AGENT,
        }
        if client_version:
            headers["x-notion-client-version"] = client_version
        return headers


def html_client_version(html: str) -> str | None:
    match = re.search(r'data-notion-version="([^"]+)"', html)
    return match.group(1) if match else None
