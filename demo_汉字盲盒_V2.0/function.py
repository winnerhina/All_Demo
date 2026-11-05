from datetime import datetime
from typing import Any
import json
import os
from pydantic import BaseModel



class ApiRequest(BaseModel):
    """接收来自 Web 端的聊天请求参数，并转换为对象"""
    message: str
    session_id: str


class ApiResponse(BaseModel):
    """统一返回给 Web 端的响应格式"""
    code: int
    message: str
    data: Any

class Session:
    """
    会话模型：一个会话 = session_id + 消息列表
    """

    def __init__(self, session_id: str, messages: list = None):
        self.session_id = session_id
        self.messages = messages if messages is not None else []

    def add_message(self, role: str, content: str) -> None:
        """往会话里追加一条消息
        :param role: 消息角色，user（用户）/ assistant（AI）
        :param content: 消息内容
        """
        self.messages.append({"role": role, "content": content})

    def to_dict(self) -> dict:
        """把会话对象转为可 JSON 序列化的字典（保存文件时用）"""
        return {"session_id": self.session_id, "messages": self.messages}

    @classmethod
    def from_dict(cls, data):
        """把字典变成 Session 对象（读取文件时用）"""
        return cls(session_id=data["session_id"], messages=data["messages"])



class SessionStorage:
    """
    会话存储：封装对 sessions 目录的 新建/保存/读取/删除/列表 操作
    """

    SESSIONS_DIR = "sessions"  # 目录常量：以后改目录名只动这一处

    def __init__(self):
        # 确保会话目录存在（服务启动时自动创建）
        if not os.path.exists(self.SESSIONS_DIR):
            os.makedirs(self.SESSIONS_DIR)

    def _path(self, session_id: str) -> str:
        """拼接会话文件的完整路径"""
        # join：自动更具当前系统生成正确的路径分隔符
        return os.path.join(self.SESSIONS_DIR, f"{session_id}.json")

    def create(self) -> Session:
        """新建一个会话并保存到文件，返回会话对象"""
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session = Session(session_id)
        self.save(session)
        return session

    def save(self, session: Session) -> None:
        """把会话对象写入 JSON 文件"""
        with open(self._path(session.session_id), "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=4)

    def load(self, session_id: str) -> Session:
        """读取会话文件"""
        try:
            with open(self._path(session_id), "r", encoding="utf-8") as f:
                return Session.from_dict(json.load(f))
        except FileNotFoundError:
            return Session(session_id)

    def exists(self, session_id: str) -> bool:
        """判断会话文件是否存在"""
        return os.path.exists(self._path(session_id))

    def delete(self, session_id: str) -> bool:
        """删除会话文件"""
        if not self.exists(session_id):
            return False
        os.remove(self._path(session_id))
        return True

    def list_ids(self) -> list:
        """返回所有会话 ID 列表（按会话 ID 倒序，最新的在最前）"""
        sessions_list = [
            name.split(".")[0]
            for name in os.listdir(self.SESSIONS_DIR)
            if name.endswith(".json")
        ]
        sessions_list.sort(reverse=True)
        return sessions_list
