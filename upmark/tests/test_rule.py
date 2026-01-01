from unittest import TestCase
from upmark.entity import Content, Raw
from upmark.rule import HashHeaderRule, EqH1Rule, EqH2Rule


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
