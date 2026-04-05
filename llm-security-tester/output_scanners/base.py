"""输出安全检测器基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ScanResult:
    """扫描结果"""
    is_safe: bool            # 是否安全
    risk_category: str       # 风险分类
    confidence: float        # 置信度 0-1
    reason: str              # 判断原因
    scanner_name: str        # 检测器名称


class BaseScanner(ABC):
    name: str = ""

    @abstractmethod
    def scan(self, prompt: str, response: str, expected: str) -> ScanResult:
        pass