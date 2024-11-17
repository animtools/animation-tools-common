import unittest
from ..src.animation_tools_common.filename_format import format_filename, parse_filename

class TestFilenameFormat(unittest.TestCase):

    def test_format_filename(self):
        template = "{TITLE}_E{EPISODE}_S{SCENE}_C{CUT}.mov"
        result = format_filename(template, "ProjectX", 5, 1, 23)
        self.assertEqual(result, "ProjectX_E05_S001_C0023.mov")

    def test_format_filename_with_invalid_chars(self):
        template = "{TITLE}:E{EPISODE}_S{SCENE}_C{CUT}.mov"
        result = format_filename(template, "Project/X", 5, 1, 23)
        self.assertEqual(result, "ProjectXE05_S001_C0023.mov")

    def test_parse_filename(self):
        template = "{TITLE}_E{EPISODE}_S{SCENE}_C{CUT}.mov"
        filename = "ProjectX_E05_S001_C0023.mov"
        result = parse_filename(template, filename)
        expected = {
            'TITLE': 'ProjectX',
            'EPISODE': 5,
            'SCENE': 1,
            'CUT': 23
        }
        self.assertEqual(result, expected)

    def test_parse_filename_mismatch(self):
        template = "{TITLE}_E{EPISODE}_S{SCENE}_C{CUT}.mov"
        filename = "ProjectX_S001_C0023.mov"
        result = parse_filename(template, filename)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()