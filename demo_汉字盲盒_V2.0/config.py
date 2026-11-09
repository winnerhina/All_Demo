"""集中配置：从环境变量读取数据库、缓存、大模型连接信息。"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# SQLite
DB_PATH = os.getenv("DB_PATH", "data/riddle.db")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
AI_REPLY_CACHE_TTL = int(os.getenv("AI_REPLY_CACHE_TTL", "86400"))

# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY_1")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
