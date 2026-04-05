"""输出检测器单元测试"""
import unittest
from unittest.mock import patch

from output_scanners.keyword_scanner import KeywordScanner
from output_scanners.llm_judge import LLMJudgeScanner


class TestKeywordScanner(unittest.TestCase):

    def test_detects_refusal(self):
        scanner = KeywordScanner()
        result = scanner.scan(
            prompt="有害请求",
            response="对不起，我无法提供这类信息",
            expected="refused"
        )
        self.assertTrue(result.is_safe)

    def test_detects_compliance(self):
        scanner = KeywordScanner()
        result = scanner.scan(
            prompt="有害请求",
            response="好的，以下是具体步骤：第一步...",
            expected="refused"
        )
        self.assertFalse(result.is_safe)


class TestLLMJudgeScanner(unittest.TestCase):

    def test_judge_error_should_be_unsafe(self):
        scanner = LLMJudgeScanner()
        with patch.object(scanner, "_call_judge", return_value={
            "safe": None,
            "category": "judge_error",
            "confidence": 0,
            "reason": "network error",
        }):
            result = scanner.scan(
                prompt="test",
                response="test",
                expected="refused",
            )

        self.assertFalse(result.is_safe)
        self.assertEqual(result.risk_category, "judge_error")


if __name__ == "__main__":
    unittest.main()
