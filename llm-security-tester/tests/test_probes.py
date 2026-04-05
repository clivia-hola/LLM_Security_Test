"""探针单元测试"""
import unittest
from probes.prompt_injection import PromptInjectionProbe
from probes.jailbreak import JailbreakProbe
from probes.content_violation import ContentViolationProbe
from probes.encoding_bypass import EncodingBypassProbe


class TestProbes(unittest.TestCase):

    def test_prompt_injection_generates_cases(self):
        probe = PromptInjectionProbe()
        cases = probe.generate_cases()
        self.assertGreater(len(cases), 0)
        for case in cases:
            self.assertIsNotNone(case.prompt)
            self.assertIn(case.expected, ["refused", "safe"])

    def test_jailbreak_generates_cases(self):
        probe = JailbreakProbe()
        cases = probe.generate_cases()
        self.assertGreater(len(cases), 0)

    def test_content_violation_has_normal_cases(self):
        """违规内容探针应包含正常样本（测误报率）"""
        probe = ContentViolationProbe()
        cases = probe.generate_cases()
        normal_cases = [c for c in cases if c.expected == "safe"]
        self.assertGreater(len(normal_cases), 0, "必须包含正常样本以测试误报率")

    def test_encoding_bypass_generates_variants(self):
        probe = EncodingBypassProbe()
        cases = probe.generate_cases()
        attack_types = {c.attack_type for c in cases}
        self.assertIn("base64_bypass", attack_types)
        self.assertIn("pinyin_bypass", attack_types)


if __name__ == '__main__':
    unittest.main()