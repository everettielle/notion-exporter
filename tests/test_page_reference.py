from __future__ import annotations

import unittest

from notion_exporter.domain.page_reference import dashify_page_id, page_id_from_url


class PageReferenceTests(unittest.TestCase):
    def test_dashify_page_id(self) -> None:
        self.assertEqual(
            dashify_page_id("352cffef661081d09d57edd12d04dbba"),
            "352cffef-6610-81d0-9d57-edd12d04dbba",
        )

    def test_page_id_from_url(self) -> None:
        self.assertEqual(
            page_id_from_url(
                "https://www.notion.so/AMS261-Lecture-24-352cffef661081d09d57edd12d04dbba"
            ),
            "352cffef-6610-81d0-9d57-edd12d04dbba",
        )


if __name__ == "__main__":
    unittest.main()
