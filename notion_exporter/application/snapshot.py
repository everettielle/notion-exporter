"""JSON snapshot helpers for hydrated pages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from notion_exporter.application.page_loader import LoadedPage


def snapshot_dict(page: LoadedPage) -> dict[str, Any]:
    return {
        "url": page.url,
        "root_id": page.root_id,
        "client_version": page.client_version,
        "blocks": page.blocks,
    }


def write_snapshot(page: LoadedPage, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot_dict(page), indent=2, ensure_ascii=False), encoding="utf-8")
