from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

from pydantic import BaseModel

import config


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
    """会话存储：每个会话保存为一个本地 JSON 文件。"""

    def __init__(self, directory=None):
        self.directory = Path(directory) if directory is not None else config.SESSIONS_DIR
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        """只接受普通会话编号，避免访问 sessions 之外的文件。"""
        if not re.fullmatch(r"[A-Za-z0-9_-]+", session_id):
            raise ValueError("无效的会话编号")
        return self.directory / f"{session_id}.json"

    def create(self) -> Session:
        """新建会话并保存，返回会话对象。"""
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        session = Session(session_id)
        self.save(session)
        return session

    def save(self, session: Session) -> None:
        """先写临时文件，写完再替换，避免写入失败损坏原有记录。"""
        path = self._path(session.session_id)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory,
                                             suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                json.dump(session.to_dict(), file, ensure_ascii=False, indent=2)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def load(self, session_id: str) -> Session:
        """读取 JSON；不存在时保留原有行为，返回空会话。"""
        path = self._path(session_id)
        if not path.is_file():
            return Session(session_id)
        with path.open(encoding="utf-8-sig") as file:
            return Session.from_dict(json.load(file))

    def exists(self, session_id: str) -> bool:
        """判断会话是否存在。"""
        return self._path(session_id).is_file()

    def delete(self, session_id: str) -> bool:
        """删除对应的 JSON 文件。"""
        try:
            self._path(session_id).unlink()
        except FileNotFoundError:
            return False
        return True

    def list_ids(self) -> list:
        """返回所有会话 ID，按时间倒序。"""
        return sorted((path.stem for path in self.directory.glob("*.json")
                       if path.is_file() and re.fullmatch(r"[A-Za-z0-9_-]+", path.stem)),
                      reverse=True)
