from datetime import datetime
import pydantic
from typing import Any
import json



# 封装响应数据类
class ApiResponse(pydantic.BaseModel):
    code: int
    message: str
    date: Any

# 封装聊天请求数据并转换为对象
class ApiRequest(pydantic.BaseModel):
    session_id: str
    message: str

# 封装获取json文件名
def get_json_name(session_id: str):
    return f"{session_id}.json"

# 封装加载json会话数据
def load_session_data(session_id: str):
    # 获取json文件名
    json_name = get_json_name(session_id)
    with open(f"sessions/{json_name}", "r", encoding="utf-8") as f:
        session_data = json.load(f)
    return session_data

# 封装保存json会话数据
def save_session_data(session_id: str, session_data: dict):
    # 获取json文件名
    json_name = get_json_name(session_id)
    with open(f"sessions/{json_name}", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)
        
# 生成会话标识
def create_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
