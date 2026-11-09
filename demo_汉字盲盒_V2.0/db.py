"""SQLite 数据访问层：会话的增删改查。"""
import json
import os
import sqlite3

import config


def _ensure_dir():
    """确保数据库文件所在目录存在。"""
    d = os.path.dirname(config.DB_PATH)
    if d and not os.path.exists(d):
        os.makedirs(d)


def get_conn():
    """创建 SQLite 连接，查询结果按字段名访问。"""
    _ensure_dir()
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化：表不存在时创建。"""
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                messages TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_session(session_id, messages):
    """保存会话：已存在则更新，不存在则插入。"""
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO sessions (session_id, messages)
            VALUES (?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                messages = excluded.messages,
                updated_at = CURRENT_TIMESTAMP
            """,
            (session_id, json.dumps(messages, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


def load_session(session_id):
    """按会话 ID 读取会话，不存在返回 None。"""
    conn = get_conn()
    try:
        cur = conn.execute(
            "SELECT session_id, messages FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return {
        "session_id": row["session_id"],
        "messages": json.loads(row["messages"] or "[]"),
    }


def delete_session(session_id):
    """删除会话，返回是否删除成功。"""
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_sessions():
    """返回所有会话 ID，按时间倒序。"""
    conn = get_conn()
    try:
        cur = conn.execute("SELECT session_id FROM sessions ORDER BY session_id DESC")
        rows = cur.fetchall()
    finally:
        conn.close()
    return [row["session_id"] for row in rows]
