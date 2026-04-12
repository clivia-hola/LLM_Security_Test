"""探针单元测试"""
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

"""探针单元测试"""
import unittest
from probes.prompt_injection import PromptInjectionProbe
from probes.jailbreak import JailbreakProbe
from probes.content_violation import ContentViolationProbe
from probes.encoding_bypass import EncodingBypassProbe
from probes.data_extraction import DataExtractionProbe   


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


class TestDataExtractionProbe(unittest.TestCase):
    def setUp(self):
        """每个测试方法运行前都会执行，避免重复初始化"""
        self.probe = DataExtractionProbe()
        self.cases = self.probe.generate_cases()

    def test_generates_cases(self):
        """基础验证：能生成case，字段不为空"""
        self.assertGreater(len(self.cases), 0)
        for case in self.cases:
            self.assertIsNotNone(case.prompt)
            self.assertIsNotNone(case.attack_type)
            self.assertIsNotNone(case.risk_category)
            self.assertIsNotNone(case.description)
            self.assertIn(case.expected, ["refused", "safe"])

    def test_has_system_prompt_leak_cases(self):
        """必须包含系统Prompt提取类攻击"""
        system_prompt_cases = [
            c for c in self.cases if "system_prompt" in c.attack_type
        ]
        self.assertGreater(len(system_prompt_cases), 0,
                           "DataExtractionProbe必须包含系统Prompt提取攻击case")

    def test_has_training_data_cases(self):
        """必须包含训练数据记忆类攻击"""
        training_cases = [
            c for c in self.cases if "training_data" in c.attack_type
        ]
        self.assertGreater(len(training_cases), 0,
                           "DataExtractionProbe必须包含训练数据记忆攻击case")

    def test_has_normal_cases(self):
        """必须包含正常case，用于计算误拒率"""
        normal_cases = [c for c in self.cases if c.expected == "safe"]
        self.assertGreater(len(normal_cases), 0,
                           "DataExtractionProbe必须包含正常case以测试误报率")

    def test_all_attack_cases_are_refused(self):
        """所有攻击case的expected必须是refused"""
        attack_cases = [c for c in self.cases if c.attack_type != "normal"]
        for case in attack_cases:
            self.assertEqual(
                case.expected, "refused"
            )


if __name__ == '__main__':
    unittest.main()
