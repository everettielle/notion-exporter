"""Render hydrated Notion blocks as Markdown."""

from __future__ import annotations

from urllib.parse import quote

from notion_exporter.application.page_loader import LoadedPage
from notion_exporter.domain.blocks import Block, BlockMap, block_children, rich_text_property
from notion_exporter.markdown.rich_text import rich_text_to_markdown, rich_text_to_plain_text


class MarkdownRenderer:
    """Markdown renderer for the block types discovered in the AMS261 page."""

    def render_page(self, page: LoadedPage) -> str:
        return self.render(page.root_id, page.blocks)

    def render(self, root_id: str, blocks: BlockMap) -> str:
        markdown = self._render_block(root_id, blocks).strip()
        return f"{markdown}\n"

    def _render_block(self, block_id: str, blocks: BlockMap) -> str:
        block = blocks.get(block_id)
        if not block:
            return ""

        block_type = block.get("type")
        if block_type == "page":
            return self._render_page_block(block, blocks)
        if block_type in {"header", "sub_header", "sub_sub_header"}:
            return self._render_heading(block_type, block, blocks)
        if block_type == "text":
            return self._render_text(block, blocks)
        if block_type == "bulleted_list":
            return self._render_list_item(block, blocks, ordered=False)
        if block_type == "numbered_list":
            return self._render_list_item(block, blocks, ordered=True)
        if block_type == "callout":
            return self._render_callout(block, blocks)
        if block_type == "divider":
            return "---"
        if block_type == "toggle":
            return self._render_toggle(block, blocks)
        if block_type in {"column_list", "column"}:
            return self._render_children(block, blocks)
        if block_type == "image":
            return self._render_image(block)
        return self._render_fallback(block, blocks)

    def _render_page_block(self, block: Block, blocks: BlockMap) -> str:
        title = self._plain_title(block) or "Untitled"
        children = self._render_children(block, blocks)
        return self._join_blocks([f"# {title}", children])

    def _render_heading(self, block_type: str, block: Block, blocks: BlockMap) -> str:
        levels = {"header": "##", "sub_header": "###", "sub_sub_header": "####"}
        heading = f"{levels[block_type]} {self._plain_title(block)}".rstrip()
        return self._join_blocks([heading, self._render_children(block, blocks)])

    def _render_text(self, block: Block, blocks: BlockMap) -> str:
        return self._join_blocks([self._title(block), self._render_children(block, blocks)])

    def _render_list_item(self, block: Block, blocks: BlockMap, ordered: bool) -> str:
        marker = "1." if ordered else "-"
        title = self._title(block)
        first_line = f"{marker} {title}".rstrip()
        children = self._render_children(block, blocks)
        if not children:
            return first_line
        return f"{first_line}\n{self._indent(children, '  ')}"

    def _render_callout(self, block: Block, blocks: BlockMap) -> str:
        icon = block.get("format", {}).get("page_icon")
        title = self._title(block)
        label = " ".join(part for part in [icon, title] if part)
        body = self._join_blocks([label, self._render_children(block, blocks)])
        if not body:
            return ""
        return "\n".join(f"> {line}" if line else ">" for line in body.splitlines())

    def _render_toggle(self, block: Block, blocks: BlockMap) -> str:
        title = self._title(block) or "Toggle"
        children = self._render_children(block, blocks)
        if not children:
            return title
        return f"<details>\n<summary>{title}</summary>\n\n{children}\n\n</details>"

    def _render_image(self, block: Block) -> str:
        source = self._plain_property(block, "source") or block.get("format", {}).get("display_source")
        alt = self._plain_property(block, "caption") or self._plain_property(block, "title") or "image"
        if not source:
            return f"![{alt}]()"
        return f"![{alt}]({self._asset_url(block, source)})"

    def _render_fallback(self, block: Block, blocks: BlockMap) -> str:
        title = self._title(block)
        children = self._render_children(block, blocks)
        if title:
            return self._join_blocks([title, children])
        return children

    def _render_children(self, block: Block, blocks: BlockMap) -> str:
        return self._join_blocks(
            self._render_block(child_id, blocks) for child_id in block_children(block)
        )

    def _title(self, block: Block) -> str:
        return rich_text_to_markdown(rich_text_property(block)).strip()

    def _plain_title(self, block: Block) -> str:
        return rich_text_to_plain_text(rich_text_property(block)).strip()

    def _plain_property(self, block: Block, name: str) -> str:
        return rich_text_to_plain_text(rich_text_property(block, name)).strip()

    def _asset_url(self, block: Block, source: str) -> str:
        if source.startswith(("http://", "https://", "data:")):
            return source
        block_id = block.get("id", "")
        space_id = block.get("space_id", "")
        encoded_source = quote(source, safe="")
        return (
            f"https://www.notion.so/image/{encoded_source}"
            f"?table=block&id={block_id}&spaceId={space_id}&width=2000&userId=&cache=v2"
        )

    @staticmethod
    def _join_blocks(blocks: object) -> str:
        parts = [str(block).strip() for block in blocks if str(block).strip()]
        return "\n\n".join(parts)

    @staticmethod
    def _indent(markdown: str, prefix: str) -> str:
        return "\n".join(f"{prefix}{line}" if line else line for line in markdown.splitlines())
