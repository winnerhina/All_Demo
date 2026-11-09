from datetime import datetime
from typing import Any

from pydantic import BaseModel

import cache
import db


class ApiRequest(BaseModel):
    """Web 端聊天请求参数。"""
    message: str
    session_id: str


class ApiResponse(BaseModel):
    """统一响应格式。"""
    code: int
    message: str
    data: Any


class Session:
    """会话模型：session_id + 消息列表。"""

    def __init__(self, session_id: str, messages: list = None):
        self.session_id = session_id
        self.messages = messages if messages is not None else []

    def add_message(self, role: str, content: str) -> None:
        """追加一条消息。"""
        self.messages.append({"role": role, "content": content})

    def to_dict(self) -> dict:
        """转为可序列化字典。"""
        return {"session_id": self.session_id, "messages": self.messages}

    @classmethod
    def from_dict(cls, data):
        """从字典构建 Session 对象。"""
        return cls(session_id=data["session_id"], messages=data["messages"])


class SessionStorage:
    """会话存储：SQLite 持久化 + Redis 缓存。"""

    def create(self) -> Session:
        """新建会话并保存，返回会话对象。"""
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session = Session(session_id)
        self.save(session)
        return session

    def save(self, session: Session) -> None:
        """保存会话到 SQLite，并同步更新 Redis 缓存。"""
        db.save_session(session.session_id, session.messages)
        cache.cache_session(session.session_id, session.to_dict())

    def load(self, session_id: str) -> Session:
        """加载会话：优先读缓存，未命中回源 SQLite；不存在返回空会话。"""
        data = cache.get_cached_session(session_id)
        if data is None:
            data = db.load_session(session_id)
        if data is None:
            return Session(session_id)
        session = Session.from_dict(data)
        cache.cache_session(session_id, data)
        return session

    def exists(self, session_id: str) -> bool:
        """判断会话是否存在。"""
        return db.load_session(session_id) is not None

    def delete(self, session_id: str) -> bool:
        """删除会话：同时删除 SQLite 记录与 Redis 缓存。"""
        ok = db.delete_session(session_id)
        cache.delete_cached_session(session_id)
        return ok

    def list_ids(self) -> list:
        """返回所有会话 ID，按时间倒序。"""
        return db.list_sessions()
