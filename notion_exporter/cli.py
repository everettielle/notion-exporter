"""Command-line interface for the Notion exporter."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import requests

from notion_exporter.application.analyzer import analyze_page, format_analysis
from notion_exporter.application.exporter import ExportPageToMarkdown
from notion_exporter.application.page_loader import PublicPageLoader
from notion_exporter.application.snapshot import write_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "analyze":
            return _analyze(args)
        if args.command == "export":
            return _export(args)
    except requests.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 1
    except requests.RequestException as exc:
        print(f"Request error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 1

    parser.error("missing command")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export public Notion pages.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Inspect a public Notion page")
    analyze.add_argument("url", help="Public Notion page URL")
    analyze.add_argument("--limit", type=int, default=500, help="loadPageChunk limit")
    analyze.add_argument("--max-outline-depth", type=int, default=3)
    analyze.add_argument("--dump-json", type=Path, help="Optional hydrated snapshot path")

    export = subparsers.add_parser("export", help="Export a public Notion page to Markdown")
    export.add_argument("url", help="Public Notion page URL")
    export.add_argument("--limit", type=int, default=500, help="loadPageChunk limit")
    export.add_argument("-o", "--output", type=Path, help="Markdown output path")

    return parser


def _analyze(args: argparse.Namespace) -> int:
    page = PublicPageLoader().load(args.url, limit=args.limit)
    analysis = analyze_page(page, max_outline_depth=args.max_outline_depth)
    print(format_analysis(page, analysis))
    if args.dump_json:
        write_snapshot(page, args.dump_json)
        print(f"Snapshot written: {args.dump_json}")
    return 0


def _export(args: argparse.Namespace) -> int:
    document = ExportPageToMarkdown().run(args.url, limit=args.limit)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(document.content, encoding="utf-8")
        print(f"Markdown written: {args.output}")
    else:
        print(document.content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
