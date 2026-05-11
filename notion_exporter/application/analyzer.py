"""Application service for summarizing a hydrated Notion page."""

from __future__ import annotations

import collections
from dataclasses import dataclass

from notion_exporter.application.page_loader import LoadedPage
from notion_exporter.domain.blocks import block_title, missing_children, walk_blocks
from notion_exporter.infrastructure.notion_client import LOAD_PAGE_CHUNK_URL


@dataclass(frozen=True)
class OutlineItem:
    depth: int
    block_id: str
    block_type: str
    title: str


@dataclass(frozen=True)
class PageAnalysis:
    title: str
    block_count: int
    missing_child_count: int
    type_counts: collections.Counter[str]
    outline: list[OutlineItem]


def analyze_page(page: LoadedPage, max_outline_depth: int = 3) -> PageAnalysis:
    type_counts: collections.Counter[str] = collections.Counter(
        block.get("type", "unknown") for block in page.blocks.values()
    )
    outline = [
        OutlineItem(
            depth=depth,
            block_id=block_id,
            block_type=block.get("type", "unknown"),
            title=block_title(block).replace("\n", " ").strip(),
        )
        for depth, block_id, block in walk_blocks(
            page.blocks,
            page.root_id,
            max_depth=max_outline_depth,
        )
    ]
    return PageAnalysis(
        title=block_title(page.root) or "(untitled)",
        block_count=len(page.blocks),
        missing_child_count=len(missing_children(page.blocks)),
        type_counts=type_counts,
        outline=outline,
    )


def format_analysis(page: LoadedPage, analysis: PageAnalysis) -> str:
    lines = [
        f"URL: {page.url}",
        f"Page ID: {page.root_id}",
        f"Notion client version: {page.client_version or 'unknown'}",
        f"Endpoint: {LOAD_PAGE_CHUNK_URL}",
        f"Title: {analysis.title}",
        f"Reachable block count: {analysis.block_count}",
        f"Missing child records: {analysis.missing_child_count}",
        "Block types:",
    ]
    lines.extend(
        f"  {block_type}: {count}" for block_type, count in analysis.type_counts.most_common()
    )
    lines.append("Outline:")
    for item in analysis.outline:
        label = item.title or f"({item.block_type})"
        lines.append(f"  {'  ' * item.depth}- {item.block_type}: {label}")
    return "\n".join(lines)
