"""探针基类"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class TestCase:
    """单个测试用例"""
    prompt: str              # 攻击Prompt
    attack_type: str         # 攻击类型
    risk_category: str       # 风险分类（对应架构图中的分类）
    expected: str            # 期望结果：refused / safe
    description: str         # 用例描述


class BaseProbe(ABC):
    """攻击探针基类"""
    name: str = ""
    description: str = ""
    # 对应架构图中的阶段
    phase: str = ""          # training / deployment / operation

    @abstractmethod
    def generate_cases(self) -> List[TestCase]:
        """生成测试用例"""
        pass