"""Redis 缓存层：会话缓存与 AI 回复缓存，连接失败自动降级。"""
import json

import redis

import config


try:
    _r = redis.Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB,
        password=config.REDIS_PASSWORD or None,
        decode_responses=True,
        socket_connect_timeout=2,
    )
    _r.ping()
    REDIS_READY = True
except Exception:
    _r = None
    REDIS_READY = False


def _session_key(session_id):
    return f"session:{session_id}"


def _ai_reply_key(msg_hash):
    return f"ai_reply:{msg_hash}"


def cache_session(session_id, session_dict):
    """缓存会话数据。"""
    if not REDIS_READY:
        return
    _r.set(_session_key(session_id), json.dumps(session_dict, ensure_ascii=False))


def get_cached_session(session_id):
    """读取缓存的会话，未命中返回 None。"""
    if not REDIS_READY:
        return None
    raw = _r.get(_session_key(session_id))
    return json.loads(raw) if raw else None


def delete_cached_session(session_id):
    """删除缓存的会话。"""
    if not REDIS_READY:
        return
    _r.delete(_session_key(session_id))


def cache_ai_reply(msg_hash, reply):
    """缓存 AI 回复并设置过期时间。"""
    if not REDIS_READY:
        return
    _r.setex(_ai_reply_key(msg_hash), config.AI_REPLY_CACHE_TTL, reply)


def get_cached_ai_reply(msg_hash):
    """读取缓存的 AI 回复，未命中返回 None。"""
    if not REDIS_READY:
        return None
    return _r.get(_ai_reply_key(msg_hash))
