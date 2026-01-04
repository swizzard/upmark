from unittest import TestCase
from upmark.entity import Content, HeaderEntity, Raw
from upmark.rule import HashHeaderRule, EqH1Rule, EqH2Rule
from upmark.parser import Parser


class TestParser(TestCase):
    def test_parse_headers(self):
        test_text = "this is a eq header\n===\n\n### this header has hashes\n\nand this has dashes\n---\n\n"
        expected_h1 = HeaderEntity(
            test_text,
            0,
            24,
            Content.raw_remainder(test_text, 0, 19),
            level=1,
            is_bof=True,
        )
        expected_h3 = HeaderEntity(
            test_text,
            24,
            51,
            Content.raw_remainder(test_text, 29, 51),
            level=3,
            is_bof=False,
        )
        expected_h2 = HeaderEntity(
            test_text,
            52,
            77,
            Content.raw_remainder(test_text, 53, 72),
            level=2,
            is_bof=False,
        )
        expected_content = Content([expected_h1, expected_h3, expected_h2])
        parser = Parser([HashHeaderRule, EqH1Rule, EqH2Rule])
        actual_content = parser.parse(test_text)
        for actual, expected in zip(actual_content.content, expected_content.content):
            self.assertEqual(actual, expected)
        # self.assertEqual(expected_content, actual_content)

    def test_parse_headers_and_text(self):
        test_text = "this is a eq header\n===\nhere is some text\n### this header has hashes\n\nand this has dashes\n---\n\n"
        expected_h1 = HeaderEntity(
            test_text,
            0,
            24,
            Content.raw_remainder(test_text, 0, 19),
            level=1,
            is_bof=True,
        )
        expected_h3 = HeaderEntity(
            test_text,
            41,
            68,
            Content.raw_remainder(test_text, 46, 68),
            level=3,
            is_bof=False,
        )
        expected_h2 = HeaderEntity(
            test_text,
            69,
            94,
            Content.raw_remainder(test_text, 70, 89),
            level=2,
            is_bof=False,
        )
        expected_raw = Raw(test_text, 24, 41)
        expected_content = Content(
            [expected_h1, expected_raw, expected_h3, expected_h2]
        )
        parser = Parser([HashHeaderRule, EqH1Rule, EqH2Rule])
        actual_content = parser.parse(test_text)
        self.assertEqual(expected_content, actual_content)
