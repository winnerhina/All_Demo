import datetime
import json
import os
from pathlib import Path
import re
import tempfile

import streamlit as st

import config


def _session_path(filename):
    """只接受普通会话编号，所有聊天记录都放在 sessions 目录。"""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", filename):
        raise ValueError("无效的会话编号")
    config.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return config.SESSIONS_DIR / f"{filename}.json"


def session_save():
    """把昵称、性格与聊天消息保存到本地 JSON 文件。"""
    if st.session_state.filename and st.session_state.messages:
        data = {
            "filename": st.session_state.filename,
            "nickname": st.session_state.nickname,
            "personality": st.session_state.personality,
            "messages": st.session_state.messages,
        }
        path = _session_path(st.session_state.filename)
        temporary = None
        try:
            # 写完临时文件后再替换，避免写入失败损坏原有记录。
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                             suffix=".tmp", delete=False) as file:
                temporary = Path(file.name)
                json.dump(data, file, ensure_ascii=False, indent=2)
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def session_filename():
    """生成会话 ID（时间戳）。"""
    return datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S-%f')


def sessions_load():
    """返回所有会话 ID 列表。"""
    config.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted((path.stem for path in config.SESSIONS_DIR.glob("*.json")
                   if path.is_file() and re.fullmatch(r"[A-Za-z0-9_-]+", path.stem)),
                  reverse=True)


def session_load(s_file):
    """从本地 JSON 恢复角色设置和聊天消息。"""
    try:
        path = _session_path(s_file)
        if not path.is_file():
            st.toast(f"会话 {s_file} 不存在", icon="⚠️")
            return

        with path.open(encoding="utf-8-sig") as file:
            data = json.load(file)

        st.session_state.nickname = data["nickname"]
        st.session_state.personality = data["personality"]
        st.session_state.filename = s_file
        st.session_state.messages = data["messages"]

    except Exception as e:
        st.toast(f"加载会话信息失败：{e}", icon="⚠️")


def session_delete(s_file):
    """删除 JSON 文件，删除当前会话时同时重置页面状态。"""
    try:
        _session_path(s_file).unlink(missing_ok=True)
        st.toast(f"会话 {s_file} 已删除", icon="🗑️")
        if s_file == st.session_state.filename:
            st.session_state.filename = session_filename()
            st.session_state.nickname = "夏美子"
            st.session_state.personality = "聪明可爱娇小的女孩"
            st.session_state.messages = []
    except Exception as e:
        st.toast(f"删除会话 {s_file} 失败：{e}", icon="⚠️")
