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
                filename TEXT NOT NULL UNIQUE,
                nickname TEXT DEFAULT '夏美子',
                personality TEXT DEFAULT '聪明可爱娇小的女孩',
                messages TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_session(filename, nickname, personality, messages):
    """保存会话：已存在则更新，不存在则插入。"""
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO sessions (filename, nickname, personality, messages)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(filename) DO UPDATE SET
                nickname = excluded.nickname,
                personality = excluded.personality,
                messages = excluded.messages,
                updated_at = CURRENT_TIMESTAMP
            """,
            (filename, nickname, personality, json.dumps(messages, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()


def load_session(filename):
    """按会话 ID 读取会话，不存在返回 None。"""
    conn = get_conn()
    try:
        cur = conn.execute(
            "SELECT filename, nickname, personality, messages FROM sessions WHERE filename = ?",
            (filename,),
        )
        row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        return None
    return {
        "filename": row["filename"],
        "nickname": row["nickname"],
        "personality": row["personality"],
        "messages": json.loads(row["messages"] or "[]"),
    }


def delete_session(filename):
    """删除会话。"""
    conn = get_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE filename = ?", (filename,))
        conn.commit()
    finally:
        conn.close()


def list_sessions():
    """返回所有会话 ID，按时间倒序。"""
    conn = get_conn()
    try:
        cur = conn.execute("SELECT filename FROM sessions ORDER BY filename DESC")
        rows = cur.fetchall()
    finally:
        conn.close()
    return [row["filename"] for row in rows]
