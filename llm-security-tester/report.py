"""报告生成模块"""
import json
import os
from datetime import datetime
from config import REPORT_DIR


def generate_report(results: list, filename: str = None):
    """生成JSON格式的详细报告"""
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

    if filename is None:
        filename = f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    filepath = os.path.join(REPORT_DIR, filename)

    # 计算统计指标
    total = len(results)
    passed = sum(1 for r in results if r["overall_passed"])
    harmful = [r for r in results if r["expected"] == "refused"]
    normal = [r for r in results if r["expected"] == "safe"]

    report = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "total_cases": total,
            "passed": passed,
            "failed": total - passed,
        },
        "metrics": {
            "defense_rate": sum(1 for r in harmful if r["overall_passed"]) / len(harmful) if harmful else 0,
            "attack_success_rate": sum(1 for r in harmful if not r["overall_passed"]) / len(harmful) if harmful else 0,
            "false_positive_rate": sum(1 for r in normal if not r["overall_passed"]) / len(normal) if normal else 0,
        },
        "details": results
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n 报告已保存: {filepath}")
    return filepath