import datetime

import streamlit as st

import cache
import db


def session_save():
    """保存当前会话到 SQLite，并同步更新 Redis 缓存。"""
    if st.session_state.filename and st.session_state.messages:
        db.save_session(
            st.session_state.filename,
            st.session_state.nickname,
            st.session_state.personality,
            st.session_state.messages,
        )
        cache.cache_session(st.session_state.filename, {
            "filename": st.session_state.filename,
            "nickname": st.session_state.nickname,
            "personality": st.session_state.personality,
            "messages": st.session_state.messages,
        })


def session_filename():
    """生成会话 ID（时间戳）。"""
    return datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')


def sessions_load():
    """返回所有会话 ID 列表。"""
    return db.list_sessions()


def session_load(s_file):
    """加载会话：优先读缓存，未命中回源 SQLite 并回填缓存。"""
    try:
        data = cache.get_cached_session(s_file)
        if data is None:
            data = db.load_session(s_file)

        if data is None:
            st.toast(f"会话 {s_file} 不存在", icon="⚠️")
            return

        st.session_state.nickname = data["nickname"]
        st.session_state.personality = data["personality"]
        st.session_state.filename = s_file
        st.session_state.messages = data["messages"]

        cache.cache_session(s_file, data)
    except Exception as e:
        st.toast(f"加载会话信息失败：{e}", icon="⚠️")


def session_delete(s_file):
    """删除会话：同时删除 SQLite 记录与 Redis 缓存。"""
    try:
        db.delete_session(s_file)
        cache.delete_cached_session(s_file)
        st.toast(f"会话 {s_file} 已删除", icon="🗑️")
        if s_file == st.session_state.filename:
            st.session_state.filename = session_filename()
            st.session_state.nickname = "夏美子"
            st.session_state.personality = "聪明可爱娇小的女孩"
            st.session_state.messages = []
    except Exception as e:
        st.toast(f"删除会话 {s_file} 失败：{e}", icon="⚠️")
