"""Domain-level helpers for Notion block records."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, TypeAlias


JsonDict: TypeAlias = dict[str, Any]
Block: TypeAlias = JsonDict
BlockMap: TypeAlias = dict[str, Block]
RichText: TypeAlias = list[Any]


def unwrap_record(record: JsonDict) -> Block | None:
    """Return a block from Notion's current record wrapper shape."""
    value = record.get("value")
    if isinstance(value, dict) and isinstance(value.get("value"), dict):
        return value["value"]
    if isinstance(value, dict):
        return value
    return None


def blocks_from_record_map(record_map: JsonDict) -> BlockMap:
    blocks: BlockMap = {}
    for block_id, record in record_map.get("block", {}).items():
        if isinstance(record, dict):
            block = unwrap_record(record)
            if block and block.get("alive", True):
                blocks[block_id] = block
    return blocks


def merge_record_map(target: BlockMap, record_map: JsonDict) -> None:
    target.update(blocks_from_record_map(record_map))


def rich_text_property(block: Block, name: str = "title") -> RichText:
    value = block.get("properties", {}).get(name)
    return value if isinstance(value, list) else []


def plain_rich_text(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return "".join(part[0] for part in value if isinstance(part, list) and part)


def block_title(block: Block) -> str:
    return plain_rich_text(rich_text_property(block))


def block_children(block: Block) -> list[str]:
    children = block.get("content")
    return children if isinstance(children, list) else []


def missing_children(blocks: BlockMap) -> list[str]:
    missing = {
        child_id
        for block in blocks.values()
        for child_id in block_children(block)
        if child_id not in blocks
    }
    return sorted(missing)


def walk_blocks(
    blocks: BlockMap,
    root_id: str,
    max_depth: int | None = None,
) -> Iterable[tuple[int, str, Block]]:
    seen: set[str] = set()

    def visit(block_id: str, depth: int) -> Iterable[tuple[int, str, Block]]:
        if block_id in seen or block_id not in blocks:
            return
        if max_depth is not None and depth > max_depth:
            return
        seen.add(block_id)
        block = blocks[block_id]
        yield depth, block_id, block
        for child_id in block_children(block):
            yield from visit(child_id, depth + 1)

    yield from visit(root_id, 0)
