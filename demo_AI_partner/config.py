"""读取大模型配置，并指定本地聊天记录的保存目录。"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 默认保存到项目目录下的 sessions/，每个会话对应一个 JSON 文件。
PROJECT_DIR = Path(__file__).resolve().parent
SESSIONS_DIR = Path(os.getenv("SESSIONS_DIR", "sessions"))
if not SESSIONS_DIR.is_absolute():
    SESSIONS_DIR = PROJECT_DIR / SESSIONS_DIR

# 大模型接口配置：密钥只放在本地 .env 中。
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY_1")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
