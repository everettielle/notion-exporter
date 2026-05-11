from __future__ import annotations

import unittest

from notion_exporter.markdown.rich_text import rich_text_to_markdown


class RichTextTests(unittest.TestCase):
    def test_basic_annotations(self) -> None:
        self.assertEqual(
            rich_text_to_markdown([["Bold", [["b"]]], [" and "], ["link", [["a", "https://x.test"]]]]),
            "**Bold** and [link](https://x.test)",
        )

    def test_equation_annotation_replaces_placeholder(self) -> None:
        self.assertEqual(
            rich_text_to_markdown([["Area element "], ["⁍", [["e", "r\\,dr\\,d\\theta"]]]]),
            "Area element $r\\,dr\\,d\\theta$",
        )


if __name__ == "__main__":
    unittest.main()
