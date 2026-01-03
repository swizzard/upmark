from unittest import TestCase
from upmark.entity import (
    Content,
    ListItemEntity,
    OrderedListEntity,
    Raw,
    UnorderedListEntity,
)
from upmark.rule import HashHeaderRule, EqH1Rule, EqH2Rule, OlRule, UlRule


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


class TestEqHRule(TestCase):
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


class TestOlRule(TestCase):
    maxDiff = None

    def test_parse_entity_no_indent(self):
        test_text = "\n\n1. one\n2. two\n"
        expected_li_1 = ListItemEntity(test_text, 1, 8, Content([Raw(test_text, 5, 8)]))
        expected_li_2 = ListItemEntity(
            test_text, 8, 15, Content([Raw(test_text, 12, 15)])
        )
        expected_ol = OrderedListEntity(
            test_text, 0, 15, [expected_li_1, expected_li_2]
        )
        actual_match = OlRule.pattern.match(test_text)
        actual_entity = OlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ol, actual_entity)

    def test_parse_entity_one_indent(self):
        test_text = "\n\n1. one\n2. two\n\t1. in one\n3. three\n"
        expected_li_1 = ListItemEntity(test_text, 1, 8, Content([Raw(test_text, 5, 8)]))
        expected_li_2 = ListItemEntity(
            test_text, 8, 15, Content([Raw(test_text, 12, 15)])
        )
        expected_li_3 = ListItemEntity(
            test_text, 26, 35, Content([Raw(test_text, 30, 35)])
        )
        expected_indented_li_1 = ListItemEntity(
            test_text, 15, 26, Content([Raw(test_text, 20, 26)])
        )
        expected_indented_ol = OrderedListEntity(
            test_text, 15, 26, [expected_indented_li_1]
        )
        expected_ol = OrderedListEntity(
            test_text,
            0,
            35,
            [expected_li_1, expected_li_2, expected_indented_ol, expected_li_3],
        )
        actual_match = OlRule.pattern.match(test_text)
        actual_entity = OlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ol, actual_entity)


class TestUlRule(TestCase):
    maxDiff = None

    def test_parse_entity_no_indent(self):
        test_text = "\n\n* one\n* two\n"
        expected_li_1 = ListItemEntity(test_text, 1, 7, Content([Raw(test_text, 4, 7)]))
        expected_li_2 = ListItemEntity(
            test_text, 7, 13, Content([Raw(test_text, 10, 13)])
        )
        expected_ul = UnorderedListEntity(
            test_text, 0, 13, [expected_li_1, expected_li_2]
        )
        actual_match = UlRule.pattern.match(test_text)
        actual_entity = UlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ul.content, actual_entity.content)

    def test_parse_entity_one_indent(self):
        test_text = "\n\n- one\n- two\n\t- in one\n- three\n"
        expected_li_1 = ListItemEntity(test_text, 1, 7, Content([Raw(test_text, 4, 7)]))
        expected_li_2 = ListItemEntity(
            test_text, 7, 13, Content([Raw(test_text, 10, 13)])
        )
        expected_li_3 = ListItemEntity(
            test_text, 23, 31, Content([Raw(test_text, 26, 31)])
        )
        expected_indented_li_1 = ListItemEntity(
            test_text, 13, 23, Content([Raw(test_text, 17, 23)])
        )
        expected_indented_ul = UnorderedListEntity(
            test_text, 13, 23, [expected_indented_li_1]
        )
        expected_ul = UnorderedListEntity(
            test_text,
            0,
            31,
            [expected_li_1, expected_li_2, expected_indented_ul, expected_li_3],
        )
        actual_match = UlRule.pattern.match(test_text)
        actual_entity = UlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ul, actual_entity)
