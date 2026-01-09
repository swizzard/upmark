from unittest import TestCase
from upmark import entity, rule
from upmark.entity import Content, Raw


class TestHashHeaderRule(TestCase):
    def test_parse_entity(self):
        test_text = "\n## this is a header\n"
        expected_content = Content([Raw(test_text, 4, 20)])
        expected_level = 2
        expected_is_bof = False
        expected_start = 0
        expected_end = 20
        actual_match = rule.HashHeaderRule.pattern.match(test_text)
        actual_entity = rule.HashHeaderRule.parse_entity(test_text, actual_match)
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
        actual_match = rule.HashHeaderRule.pattern.match(test_text)
        actual_entity = rule.HashHeaderRule.parse_entity(test_text, actual_match)
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
        actual_match = rule.EqH1Rule.pattern.match(test_text)
        actual_entity = rule.EqH1Rule.parse_entity(test_text, actual_match)
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
        actual_match = rule.EqH2Rule.pattern.match(test_text)
        actual_entity = rule.EqH2Rule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_content, actual_entity.content)
        self.assertEqual(expected_level, actual_entity.level)
        self.assertEqual(expected_is_bof, actual_entity.is_bof)
        self.assertEqual(expected_start, actual_entity.start)
        self.assertEqual(expected_end, actual_entity.end)


class TestOlRule(TestCase):
    def test_parse_entity_no_indent(self):
        test_text = "\n\n1. one\n2. two\n"
        expected_li_1 = entity.ListItemEntity(
            test_text, 1, 8, Content([Raw(test_text, 5, 8)])
        )
        expected_li_2 = entity.ListItemEntity(
            test_text, 8, 15, Content([Raw(test_text, 12, 15)])
        )
        expected_ol = entity.OrderedListEntity(
            test_text, 0, 15, [expected_li_1, expected_li_2]
        )
        actual_match = rule.OlRule.pattern.match(test_text)
        actual_entity = rule.OlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ol, actual_entity)

    def test_parse_entity_one_indent(self):
        test_text = "\n\n1. one\n2. two\n\t1. in one\n3. three\n"
        expected_li_1 = entity.ListItemEntity(
            test_text, 1, 8, Content([Raw(test_text, 5, 8)])
        )
        expected_li_2 = entity.ListItemEntity(
            test_text, 8, 15, Content([Raw(test_text, 12, 15)])
        )
        expected_li_3 = entity.ListItemEntity(
            test_text, 26, 35, Content([Raw(test_text, 30, 35)])
        )
        expected_indented_li_1 = entity.ListItemEntity(
            test_text, 15, 26, Content([Raw(test_text, 20, 26)])
        )
        expected_indented_ol = entity.OrderedListEntity(
            test_text, 15, 26, [expected_indented_li_1]
        )
        expected_ol = entity.OrderedListEntity(
            test_text,
            0,
            35,
            [expected_li_1, expected_li_2, expected_indented_ol, expected_li_3],
        )
        actual_match = rule.OlRule.pattern.match(test_text)
        actual_entity = rule.OlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ol, actual_entity)


class TestUlRule(TestCase):
    maxDiff = None

    def test_parse_entity_no_indent(self):
        test_text = "\n\n* one\n* two\n"
        expected_li_1 = entity.ListItemEntity(
            test_text, 1, 7, Content([Raw(test_text, 4, 7)])
        )
        expected_li_2 = entity.ListItemEntity(
            test_text, 7, 13, Content([Raw(test_text, 10, 13)])
        )
        expected_ul = entity.UnorderedListEntity(
            test_text, 0, 13, [expected_li_1, expected_li_2]
        )
        actual_match = rule.UlRule.pattern.match(test_text)
        actual_entity = rule.UlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ul.content, actual_entity.content)

    def test_parse_entity_one_indent(self):
        test_text = "\n\n- one\n- two\n\t- in one\n- three\n"
        expected_li_1 = entity.ListItemEntity(
            test_text, 1, 7, Content([Raw(test_text, 4, 7)])
        )
        expected_li_2 = entity.ListItemEntity(
            test_text, 7, 13, Content([Raw(test_text, 10, 13)])
        )
        expected_li_3 = entity.ListItemEntity(
            test_text, 23, 31, Content([Raw(test_text, 26, 31)])
        )
        expected_indented_li_1 = entity.ListItemEntity(
            test_text, 13, 23, Content([Raw(test_text, 17, 23)])
        )
        expected_indented_ul = entity.UnorderedListEntity(
            test_text, 13, 23, [expected_indented_li_1]
        )
        expected_ul = entity.UnorderedListEntity(
            test_text,
            0,
            31,
            [expected_li_1, expected_li_2, expected_indented_ul, expected_li_3],
        )
        actual_match = rule.UlRule.pattern.match(test_text)
        actual_entity = rule.UlRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_ul, actual_entity)


class TestFencedPreRule(TestCase):
    def test_parse_entity_no_lang(self):
        test_text = "\n```\nthis\ttext\nis _pre-formatted_```\n"
        expected_entity = entity.FencedPreEntity(
            test_text, 0, 37, None, "this\ttext\nis _pre-formatted_"
        )
        actual_match = rule.FencedPreRule.pattern.match(test_text)
        actual_entity = rule.FencedPreRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_entity, actual_entity)

    def test_parse_entity_lang(self):
        test_text = "\n```python\nthis\ttext\nis _pre-formatted_```\n"
        expected_entity = entity.FencedPreEntity(
            test_text, 0, 43, "python", "this\ttext\nis _pre-formatted_"
        )
        actual_match = rule.FencedPreRule.pattern.match(test_text)
        actual_entity = rule.FencedPreRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_entity, actual_entity)


class TestIndentedPreRule(TestCase):
    def test_parse_entity(self):
        test_text = "\n\n    _this text_ is\n    *pre-formatted*\n\n"
        expected_line_1 = entity.IndentedPreLineEntity(test_text, 6, 19)
        expected_line_2 = entity.IndentedPreLineEntity(test_text, 25, 39)
        expected_entity = entity.IndentedPreEntity(
            test_text, 0, 41, [expected_line_1, expected_line_2]
        )
        actual_match = rule.IndentedPreRule.pattern.match(test_text)
        actual_entity = rule.IndentedPreRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_entity, actual_entity)


class TestBlockQuoteRule(TestCase):
    def test_parse_entity(self):
        test_text = "\n\n> this is blockquoted\n>\n> so is this\n"
        expected_line_1 = entity.BlockQuoteLineEntity(test_text, 4, 23)
        expected_line_2 = entity.BlockQuoteLineEntity(test_text, 25, 25)
        expected_line_3 = entity.BlockQuoteLineEntity(test_text, 28, 38)
        expected_entity = entity.BlockQuoteEntity(
            test_text, 0, 41, [expected_line_1, expected_line_2, expected_line_3]
        )
        actual_match = rule.BlockQuoteRule.pattern.match(test_text)
        actual_entity = rule.BlockQuoteRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_entity.content, actual_entity.content)


class TestEmRule(TestCase):
    def test_parse_entity(self):
        test_text = "_emphasized text_"
        expected_entity = entity.EmEntity(test_text, 0, 17, [Raw(test_text, 1, 16)])
        actual_match = rule.EmRule.pattern.match(test_text)
        actual_entity = rule.EmRule.parse_entity(test_text, actual_match)
        self.assertEqual(expected_entity, actual_entity)
