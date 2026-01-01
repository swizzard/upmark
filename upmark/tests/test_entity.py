from unittest import TestCase
from upmark.entity import Content, EmEntity, HeaderEntity, ParagraphEntity, Raw


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
