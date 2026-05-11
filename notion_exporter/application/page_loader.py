"""Use case for loading and hydrating a public Notion page."""

from __future__ import annotations

from dataclasses import dataclass

from notion_exporter.domain.blocks import Block, BlockMap, block_children, merge_record_map
from notion_exporter.domain.page_reference import PageReference
from notion_exporter.infrastructure.notion_client import NotionClient, html_client_version


@dataclass(frozen=True)
class LoadedPage:
    url: str
    root_id: str
    client_version: str | None
    blocks: BlockMap

    @property
    def root(self) -> Block:
        return self.blocks[self.root_id]


class PublicPageLoader:
    """Loads a public page and recursively hydrates reachable child blocks."""

    def __init__(self, client: NotionClient | None = None) -> None:
        self.client = client or NotionClient()

    def load(self, url: str, limit: int = 500) -> LoadedPage:
        reference = PageReference.from_url(url)
        html = self.client.fetch_public_html(url)
        client_version = html_client_version(html)
        blocks = self._hydrate_reachable_blocks(reference, client_version, limit)
        return LoadedPage(
            url=url,
            root_id=reference.page_id,
            client_version=client_version,
            blocks=blocks,
        )

    def _hydrate_reachable_blocks(
        self,
        reference: PageReference,
        client_version: str | None,
        limit: int,
    ) -> BlockMap:
        blocks: BlockMap = {}
        desired_ids: set[str] = {reference.page_id}
        loaded_subtrees: set[str] = set()

        while True:
            to_load = [
                block_id
                for block_id in desired_ids
                if block_id not in loaded_subtrees
                and (
                    block_id == reference.page_id
                    or block_id not in blocks
                    or any(child_id not in blocks for child_id in block_children(blocks[block_id]))
                )
            ]
            if not to_load:
                break

            for block_id in sorted(to_load):
                data = self.client.load_page_chunk(
                    block_id=block_id,
                    referer=reference.url,
                    client_version=client_version,
                    limit=limit,
                )
                merge_record_map(blocks, data.get("recordMap", {}))
                loaded_subtrees.add(block_id)

            changed = True
            while changed:
                changed = False
                for block_id in list(desired_ids):
                    for child_id in block_children(blocks.get(block_id, {})):
                        if child_id not in desired_ids:
                            desired_ids.add(child_id)
                            changed = True

        return {block_id: blocks[block_id] for block_id in desired_ids if block_id in blocks}
