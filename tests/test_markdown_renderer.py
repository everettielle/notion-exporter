from __future__ import annotations

import unittest

from notion_exporter.markdown.renderer import MarkdownRenderer


class MarkdownRendererTests(unittest.TestCase):
    def test_renders_page_and_children(self) -> None:
        blocks = {
            "page": {
                "id": "page",
                "type": "page",
                "properties": {"title": [["Demo"]]},
                "content": ["h", "p"],
            },
            "h": {"id": "h", "type": "header", "properties": {"title": [["Section"]]}},
            "p": {
                "id": "p",
                "type": "text",
                "properties": {"title": [["x"], ["⁍", [["e", "y"]]]]},
            },
        }

        self.assertEqual(
            MarkdownRenderer().render("page", blocks),
            "# Demo\n\n## Section\n\nx$y$\n",
        )


if __name__ == "__main__":
    unittest.main()
