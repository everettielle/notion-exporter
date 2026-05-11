"""Application use case for exporting a public Notion page to Markdown."""

from __future__ import annotations

from dataclasses import dataclass

from notion_exporter.application.page_loader import LoadedPage, PublicPageLoader
from notion_exporter.domain.blocks import block_title
from notion_exporter.markdown.renderer import MarkdownRenderer


@dataclass(frozen=True)
class MarkdownDocument:
    title: str
    content: str
    page: LoadedPage


class ExportPageToMarkdown:
    def __init__(
        self,
        loader: PublicPageLoader | None = None,
        renderer: MarkdownRenderer | None = None,
    ) -> None:
        self.loader = loader or PublicPageLoader()
        self.renderer = renderer or MarkdownRenderer()

    def run(self, url: str, limit: int = 500) -> MarkdownDocument:
        page = self.loader.load(url, limit=limit)
        return MarkdownDocument(
            title=block_title(page.root) or "Untitled",
            content=self.renderer.render_page(page),
            page=page,
        )
