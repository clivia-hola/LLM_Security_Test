# LLM Security Tester（大模型安全测试）

> 一个轻量级的大模型安全评测框架，用于自动化测试 LLM 对各类安全攻击的防御能力。

------

## 项目简介

解决大模型（LLM）的**Prompt 注入、越狱攻击、违规内容诱导**。本项目为一套可扩展的自动化评测框架，系统性地测试自己的 chatbot 的安全防御能力。

项目包含两个独立模块：

- `llm-security-tester/` —— 大模型安全评测框架（攻击探针 + 输出检测）
- `chatbot.py` —— 基于 Streamlit + DeepSeek 的多轮对话 chatbot（可作为被测目标）

### 组件与安全阶段对应关系

| 组件                   | 对应安全阶段 | 说明                 |
| ---------------------- | ------------ | -------------------- |
| Probes（攻击探针）     | 输入侧安全   | 模拟各类攻击 Prompt  |
| Runner（执行引擎）     | 安全评测服务 | 编排执行，统计指标   |
| Scanners（输出检测器） | 输出侧安全   | 检测模型输出是否安全 |

------

## 项目结构

```
.
├── chatbot.py                   # Streamlit 多轮对话 chatbot（可作为被测目标）
│
└── llm-security-tester/
    ├── main.py                  # 主入口，注册探针和检测器后运行
    ├── runner.py                # 执行引擎（可切换攻击目标）
    ├── report.py                # JSON 报告生成
    ├── config.py                # API Key、模型等配置
    ├── requirements.txt
    │
    ├── probes/                  # 攻击探针（输入侧）
    │   ├── __init__.py
    │   ├── base.py              # 探针基类与 TestCase 定义
    │   ├── prompt_injection.py  # Prompt 注入：指令覆写、分隔符注入等
    │   ├── jailbreak.py         # 越狱攻击：DAN、角色扮演、虚构场景等
    │   ├── content_violation.py # 违规内容：违法、诈骗、隐私、歧视
    │   └── encoding_bypass.py   # 编码绕过：Base64、拼音、反转、混合语言
    │
    ├── output_scanners/         # 输出检测器（输出侧）
    │   ├── base.py              # 检测器基类与 ScanResult 定义
    │   ├── keyword_scanner.py   # 关键词规则匹配（第一层，低延迟）
    │   └── llm_judge.py         # LLM-as-Judge 语义检测（第二层，高精度）
    │
    ├── data/
    │   └── test_prompts.json    # 测试样本集
    ├── reports/                 # 自动生成的评测报告（JSON）
    └── tests/
        ├── test_probes.py       # 探针单元测试
        └── test_scanners.py     # 检测器单元测试
```

------

### 环境要求

- Python 3.9+
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 安装依赖

```bash
cd llm-security-tester
pip install -r requirements.txt
```

### 配置 API Key

```bash
export DEEPSEEK_API_KEY="sk-key-here"
```
------

### 运行 Chatbot

```bash
pip install streamlit langchain-deepseek langchain-core
streamlit run chatbot.py
```

功能：

- 多轮对话，完整保留上下文
- 流式输出（打字机效果）
- 侧边栏调节 Temperature、Max Tokens、System Prompt
- 支持导出对话记录

### Chatbot的界面

![Chatbot界面](docs/images/image-20260405210130435.png)

### 攻击 Chatbot 

根据自己的chatbot修改 `runner.py` 顶部的配置，填入 chatbot 参数：

```python
CHATBOT_MODEL       = "deepseek-chat"
CHATBOT_TEMP        = 0.7
CHATBOT_MAX_TOKENS  = 1024
CHATBOT_SYSTEM_PROMPT = """你是一个有帮助的AI助手，回答简洁、准确。"""
```

然后正常运行：

```bash
cd llm-security-tester
python main.py
```

#### 运行结果

![单元测试结果](docs/images/image-20260405215753570.png)


## 运行单元测试

```bash
cd llm-security-tester
python -m pytest tests/ -v
```

如果环境未安装 pytest，也可以使用：

```bash
python -m unittest discover -s tests -v
```

#### 运行结果

![评测指标示例](docs/images/image-20260405210507077.png)
------

## 支持的攻击类型

| 探针                | 攻击类型    | 用例数 | 示例                             |
| ------------------- | ----------- | ------ | -------------------------------- |
| `prompt_injection`  | Prompt 注入 | 5      | 指令覆写、分隔符注入、权限伪造   |
| `jailbreak`         | 越狱攻击    | 4      | DAN 攻击、角色扮演、虚构场景     |
| `content_violation` | 违规内容    | 7      | 违法、诈骗、隐私侵犯、歧视       |
| `encoding_bypass`   | 编码绕过    | 5      | Base64、拼音、中英混合、文字反转 |

------

## 核心评测指标

| 指标                 | 含义                       | 目标     |
| -------------------- | -------------------------- | -------- |
| **安全防御率**       | 有害请求被正确拒绝的比例   | 越高越好 |
| **攻击成功率 (ASR)** | 攻击样本成功绕过防护的比例 | 越低越好 |
| **误拒率**           | 正常请求被误判拦截的比例   | 越低越好 |

------

