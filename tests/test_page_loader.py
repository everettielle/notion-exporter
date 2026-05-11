from __future__ import annotations

import unittest
from typing import Any

from notion_exporter.application.page_loader import PublicPageLoader
from notion_exporter.domain.blocks import missing_children


def record(block: dict[str, Any]) -> dict[str, Any]:
    return {"value": {"value": block}}


class FakeNotionClient:
    def fetch_public_html(self, _url: str) -> str:
        return '<html data-notion-version="test"></html>'

    def load_page_chunk(
        self,
        block_id: str,
        referer: str,
        client_version: str | None,
        limit: int,
    ) -> dict[str, Any]:
        del referer, client_version, limit
        if block_id == "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa":
            blocks = {
                block_id: record(
                    {
                        "id": block_id,
                        "type": "page",
                        "properties": {"title": [["Root"]]},
                        "content": ["bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"],
                    }
                ),
                "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb": record(
                    {
                        "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                        "type": "sub_header",
                        "properties": {"title": [["Section"]]},
                        "content": ["cccccccc-cccc-cccc-cccc-cccccccccccc"],
                    }
                ),
                "cccccccc-cccc-cccc-cccc-cccccccccccc": record(
                    {
                        "id": "cccccccc-cccc-cccc-cccc-cccccccccccc",
                        "type": "callout",
                        "content": ["dddddddd-dddd-dddd-dddd-dddddddddddd"],
                    }
                ),
                "dddddddd-dddd-dddd-dddd-dddddddddddd": record(
                    {
                        "id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
                        "type": "text",
                        "properties": {"title": [["Nested text"]]},
                    }
                ),
            }
        else:
            blocks = {}
        return {"recordMap": {"block": blocks}}


class PageLoaderTests(unittest.TestCase):
    def test_keeps_descendants_discovered_with_newly_discovered_parent(self) -> None:
        loader = PublicPageLoader(client=FakeNotionClient())  # type: ignore[arg-type]
        page = loader.load("https://www.notion.so/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

        self.assertIn("dddddddd-dddd-dddd-dddd-dddddddddddd", page.blocks)
        self.assertEqual(missing_children(page.blocks), [])


if __name__ == "__main__":
    unittest.main()
