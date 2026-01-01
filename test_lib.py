from unittest import TestCase
from lib import (
    Content,
    EmEntity,
    EqH1Rule,
    EqH2Rule,
    HashHeaderRule,
    HeaderEntity,
    Raw,
    ParagraphEntity,
    Parser,
)


class TestRaw(TestCase):
    def test_from_str(self):
        test_str = "this is a 34-character test string"
        actual = Raw.from_str(test_str)
        self.assertEqual(0, actual.start)
        self.assertEqual(34, actual.end)
        self.assertEqual(test_str, actual.text)

    def test_get_slice(self):
        test_str = "this is a 34-character test string"
        orig = Raw(test_str, 0, 33)
        start_offset = 5
        end_offset = -7
        expected_start = 5
        expected_end = 26
        actual = orig.get_slice(start_offset, end_offset)
        self.assertEqual(expected_start, actual.start)
        self.assertEqual(expected_end, actual.end)
        self.assertEqual(test_str, actual.text)


class TestEmEntity(TestCase):
    def test_str(self):
        test_text = "_test string_"
        content = Content([Raw(test_text, 1, 12)])
        actual = EmEntity(test_text, 0, 13, content)
        expected_str = "<em>test string</em>"
        self.assertEqual(expected_str, actual.to_string())


class TestParagraphEntity(TestCase):
    def test_str(self):
        test_text = "\n\nthis is a paragraph of text\n"
        content = Content([Raw(test_text, 2, 30)])
        actual = ParagraphEntity(test_text, 0, 30, content)
        expected_str = "\n<p>this is a paragraph of text\n</p>\n"
        self.assertEqual(expected_str, actual.to_string())


class TestHeaderEntity(TestCase):
    def test_str(self):
        test_text = "\n# this is a header\n"
        content = Content([Raw(test_text, 3, 19)])
        actual = HeaderEntity(test_text, 0, 19, content, level=1, is_bof=False)
        expected_str = "\n<h1>this is a header</h1>\n"
        self.assertEqual(expected_str, actual.to_string())

    def test_str_bof(self):
        test_text = "## this is a header\n"
        content = Content([Raw(test_text, 3, 19)])
        actual = HeaderEntity(test_text, 0, 19, content, level=2, is_bof=True)
        expected_str = "<h2>this is a header</h2>\n"
        self.assertEqual(expected_str, actual.to_string())


class TestHashHeaderRule(TestCase):
    def test_parse_entity(self):
        test_text = "\n## this is a header\n"
        expected_content = Content([Raw(test_text, 4, 20)])
        expected_level = 2
        expected_is_bof = False
        expected_start = 0
        expected_end = 20
        actual_match = HashHeaderRule.pattern.match(test_text)
        actual_entity = HashHeaderRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_content, actual_entity.content)
        self.assertEqual(expected_level, actual_entity.level)
        self.assertEqual(expected_is_bof, actual_entity.is_bof)
        self.assertEqual(expected_start, actual_entity.start)
        self.assertEqual(expected_end, actual_entity.end)

    def test_parse_entity_is_bof(self):
        test_text = "### this is a header\n"
        expected_content = Content([Raw(test_text, 4, 20)])
        expected_level = 3
        expected_is_bof = True
        expected_start = 0
        expected_end = 20
        actual_match = HashHeaderRule.pattern.match(test_text)
        actual_entity = HashHeaderRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_content, actual_entity.content)
        self.assertEqual(expected_level, actual_entity.level)
        self.assertEqual(expected_is_bof, actual_entity.is_bof)
        self.assertEqual(expected_start, actual_entity.start)
        self.assertEqual(expected_end, actual_entity.end)


class TestEqH1Rule(TestCase):
    def test_parse_entity(self):
        test_text = "this is a header\n==\nmore content"
        expected_content = Content([Raw(test_text, 0, 16)])
        expected_level = 1
        expected_is_bof = True
        expected_start = 0
        expected_end = 20
        actual_match = EqH1Rule.pattern.match(test_text)
        actual_entity = EqH1Rule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_content, actual_entity.content)
        self.assertEqual(expected_level, actual_entity.level)
        self.assertEqual(expected_is_bof, actual_entity.is_bof)
        self.assertEqual(expected_start, actual_entity.start)
        self.assertEqual(expected_end, actual_entity.end)

    def test_parse_entity_is_bof(self):
        test_text = "\nthis is a header\n--\nmore content"
        expected_content = Content([Raw(test_text, 1, 17)])
        expected_level = 2
        expected_is_bof = False
        expected_start = 0
        expected_end = 21
        actual_match = EqH2Rule.pattern.match(test_text)
        actual_entity = EqH2Rule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_content, actual_entity.content)
        self.assertEqual(expected_level, actual_entity.level)
        self.assertEqual(expected_is_bof, actual_entity.is_bof)
        self.assertEqual(expected_start, actual_entity.start)
        self.assertEqual(expected_end, actual_entity.end)


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
        for actual, expected in zip(actual_content.content, expected_content.content):
            self.assertEqual(actual, expected)
        # self.assertEqual(expected_content, actual_content)
