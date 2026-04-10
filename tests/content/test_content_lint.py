import unittest

from tools.content_lint import run_content_lint


class ContentLintTests(unittest.TestCase):
    def test_content_lint_has_no_issues(self):
        issues = run_content_lint()
        self.assertEqual(issues, [])


if __name__ == "__main__":
    unittest.main()
