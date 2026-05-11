"""Page identity parsing independent of any HTTP client."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import urlparse


@dataclass(frozen=True)
class PageReference:
    """A public Notion page URL and its canonical UUID."""

    url: str
    page_id: str

    @classmethod
    def from_url(cls, url: str) -> "PageReference":
        return cls(url=url, page_id=page_id_from_url(url))


def dashify_page_id(raw_id: str) -> str:
    clean = raw_id.replace("-", "")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", clean):
        raise ValueError(f"Expected a 32-character Notion page id, got {raw_id!r}")
    return (
        f"{clean[0:8]}-{clean[8:12]}-{clean[12:16]}-"
        f"{clean[16:20]}-{clean[20:32]}"
    ).lower()


def page_id_from_url(url: str) -> str:
    path = urlparse(url).path.rstrip("/")
    match = re.search(r"([0-9a-fA-F]{32})$", path)
    if not match:
        raise ValueError(f"Could not find a Notion page id at the end of {url!r}")
    return dashify_page_id(match.group(1))
