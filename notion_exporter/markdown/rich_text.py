"""Convert Notion rich text arrays to Markdown."""

from __future__ import annotations

from typing import Any

from notion_exporter.domain.blocks import plain_rich_text


def rich_text_to_markdown(value: Any) -> str:
    if not isinstance(value, list):
        return ""
    return "".join(_segment_to_markdown(segment) for segment in value if isinstance(segment, list))


def _segment_to_markdown(segment: list[Any]) -> str:
    if not segment:
        return ""

    text = str(segment[0])
    annotations = _annotation_map(segment[1] if len(segment) > 1 else [])

    if "e" in annotations:
        text = f"${annotations['e']}$"
    elif "c" in annotations:
        text = f"`{text.replace('`', '\\`')}`"
    else:
        if "b" in annotations:
            text = f"**{text}**"
        if "i" in annotations:
            text = f"*{text}*"
        if "s" in annotations:
            text = f"~~{text}~~"

    link = annotations.get("a")
    if link:
        text = f"[{text}]({link})"

    return text


def rich_text_to_plain_text(value: Any) -> str:
    return plain_rich_text(value)


def _annotation_map(raw_annotations: Any) -> dict[str, Any]:
    if not isinstance(raw_annotations, list):
        return {}

    annotations: dict[str, Any] = {}
    for annotation in raw_annotations:
        if not isinstance(annotation, list) or not annotation:
            continue
        key = annotation[0]
        annotations[key] = annotation[1] if len(annotation) > 1 else True
    return annotations
