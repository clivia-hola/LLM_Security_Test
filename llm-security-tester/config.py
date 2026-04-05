"""配置文件"""
import os


# DeepSeek API配置
DEEPSEEK_API_URL = os.environ.get(
	"DEEPSEEK_API_URL",
	"https://api.deepseek.com/chat/completions"
)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-chat"

# 测试配置
REQUEST_TIMEOUT = 30        # 请求超时（秒）
MAX_TOKENS = 500            # 最大输出token
REPORT_DIR = "reports"      # 报告输出目录