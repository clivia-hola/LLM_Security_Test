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
from output_scanners.keyword_scanner import KeywordScanner
from output_scanners.llm_judge import LLMJudgeScanner
from runner import SecurityTestRunner
from report import generate_report


def main():
    # 注册攻击探针（输入侧测试）
    probes = [
        PromptInjectionProbe(),
        JailbreakProbe(),
        ContentViolationProbe(),
        EncodingBypassProbe(),
    ]

    # 注册输出检测器（输出侧检测）
    scanners = [
        KeywordScanner(),       # 第一层：规则快速检测（低延迟）
        LLMJudgeScanner(),      # 第二层：LLM语义检测（高准确率）
    ]

    # 创建执行引擎并运行
    runner = SecurityTestRunner(probes=probes, scanners=scanners)
    results = runner.run()

    # 生成报告
    generate_report(results)


if __name__ == "__main__":
    main()
