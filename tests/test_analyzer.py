import unittest

from analyzer import analyze_error


class AnalyzerTests(unittest.TestCase):
    def test_type_error_and_line_number(self):
        text = 'File "main.py", line 2, in <module>\nTypeError: unsupported operand type(s) for +: \'int\' and \'str\''
        result = analyze_error(text)
        self.assertEqual(result["error_type"], "TypeError")
        self.assertEqual(result["line"], 2)

    def test_name_error(self):
        result = analyze_error("NameError: name 'totl' is not defined")
        self.assertEqual(result["error_type"], "NameError")
        self.assertIn("totl", result["suggestion"])

    def test_zero_division(self):
        result = analyze_error("ZeroDivisionError: division by zero")
        self.assertEqual(result["error_type"], "ZeroDivisionError")

    def test_last_exception_wins(self):
        result = analyze_error("ValueError: first\nTypeError: second")
        self.assertEqual(result["error_type"], "TypeError")

    def test_missing_traceback(self):
        result = analyze_error("")
        self.assertEqual(result["error_type"], "No error supplied")

    def test_unrecognized_text(self):
        result = analyze_error("Program crashed")
        self.assertEqual(result["error_type"], "UnknownError")

    def test_full_file_path(self):
        result = analyze_error('File "C:\\Users\\demo\\main.py", line 17, in test\nIndexError: list index out of range')
        self.assertEqual(result["line"], 17)
        self.assertEqual(result["error_type"], "IndexError")

    def test_module_not_found(self):
        result = analyze_error("ModuleNotFoundError: No module named 'numpy'")
        self.assertIn("numpy", result["suggestion"])


if __name__ == "__main__":
    unittest.main()
