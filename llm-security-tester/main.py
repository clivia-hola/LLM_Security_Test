"""
LLM安全评测工具 - 主入口

使用方法:
  export DEEPSEEK_API_KEY="your-key"
  python main.py
"""

from probes.prompt_injection import PromptInjectionProbe
from probes.jailbreak import JailbreakProbe
from probes.content_violation import ContentViolationProbe
from probes.encoding_bypass import EncodingBypassProbe
from probes.data_extraction import DataExtractionProbe    

from output_scanners.keyword_scanner import KeywordScanner
from output_scanners.llm_judge import LLMJudgeScanner
from runner import SecurityTestRunner
from report import generate_report


def main():
    # 注册攻击探针
    probes = [
        PromptInjectionProbe(),    # Prompt注入，5个case
        JailbreakProbe(),          # 越狱攻击，4个case
        ContentViolationProbe(),   # 违规内容，7个case（含3个正常case）
        EncodingBypassProbe(),     # 编码绕过，5个case
        DataExtractionProbe(),     # 数据提取攻击，10个case（含2个正常case）
    ]
    #总计：21 + 10 = 31个case，其中攻击case 26个，正常case 5个

    # 注册输出检测器
    scanners = [
        KeywordScanner(),       # 第一层：规则快速检测（低延迟）
        LLMJudgeScanner(),      # 第二层：LLM语义检测（高准确率，JSON解析）
    ]

    # 创建执行引擎并运行
    runner = SecurityTestRunner(probes=probes, scanners=scanners)
    results = runner.run()

    # 生成报告
    generate_report(results)


if __name__ == "__main__":
    main()



TEST_PROBES_CONTENT = '''"""探针单元测试"""
import unittest
from probes.prompt_injection import PromptInjectionProbe
from probes.jailbreak import JailbreakProbe
from probes.content_violation import ContentViolationProbe
from probes.encoding_bypass import EncodingBypassProbe
from probes.data_extraction import DataExtractionProbe   


class TestProbes(unittest.TestCase):
    # 以下4个测试方法和原版完全一样，不改动
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


# 测试DataExtractionProbe
class TestDataExtractionProbe(unittest.TestCase):

    def test_generates_cases(self):
        """基础测试：能生成case，且字段不为空"""
        probe = DataExtractionProbe()
        cases = probe.generate_cases()
        self.assertGreater(len(cases), 0)
        for case in cases:
            self.assertIsNotNone(case.prompt)
            self.assertIn(case.expected, ["refused", "safe"])

    def test_has_system_prompt_leak_cases(self):
        """必须包含系统Prompt提取类攻击"""
        probe = DataExtractionProbe()
        cases = probe.generate_cases()
        system_prompt_cases = [
            c for c in cases
            if "system_prompt" in c.attack_type
        ]
        self.assertGreater(
            len(system_prompt_cases), 0,
            "DataExtractionProbe必须包含系统Prompt提取攻击case"
        )

    def test_has_training_data_cases(self):
        """必须包含训练数据记忆类攻击"""
        probe = DataExtractionProbe()
        cases = probe.generate_cases()
        training_cases = [
            c for c in cases
            if "training_data" in c.attack_type
        ]
        self.assertGreater(
            len(training_cases), 0,
            "DataExtractionProbe必须包含训练数据记忆攻击case"
        )

    def test_has_normal_cases_for_false_positive(self):
        """必须包含正常case，用于测试误拒率"""
        probe = DataExtractionProbe()
        cases = probe.generate_cases()
        normal_cases = [c for c in cases if c.expected == "safe"]
        self.assertGreater(
            len(normal_cases), 0,
            "DataExtractionProbe必须包含正常case以测试误报率"
        )

    def test_all_cases_have_risk_category(self):
        """每个case都应该有risk_category字段"""
        probe = DataExtractionProbe()
        cases = probe.generate_cases()
        for case in cases:
            self.assertIsNotNone(
                case.risk_category,
                f"case '{case.description}' 缺少 risk_category 字段"
            )


if __name__ == "__main__":
    unittest.main()
'''
