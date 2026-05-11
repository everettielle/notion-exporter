# Notion Exporter

Convert a public Notion page response into Markdown.

## Usage

Analyze a public page:

```bash
source .venv/bin/activate
python -m notion_exporter.cli analyze "https://www.notion.so/URL"
```

Export a public page:

```bash
source .venv/bin/activate
python -m notion_exporter.cli export "https://www.notion.so/URL" -o MARKDOWN.md
```

## Architecture

The code is split by responsibility:

- `notion_exporter/domain`: pure helpers for page IDs and block records.
- `notion_exporter/infrastructure`: HTTP adapter for Notion web endpoints.
- `notion_exporter/application`: use cases for loading, hydration, analysis, snapshots, and export orchestration.
- `notion_exporter/markdown`: rich text and block rendering into Markdown.
- `notion_exporter/cli.py`: command-line wiring only.
- `scripts`: thin compatibility wrappers.
- `tests`: focused unit tests for stable behavior.

The dependency direction is intentionally inward: infrastructure and CLI depend
on application/domain code, while domain helpers do not know about requests,
files, or Markdown.
