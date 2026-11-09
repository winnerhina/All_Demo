"""验证本地聊天记录与接口流程；模型回复使用模拟数据，不发送外部请求。"""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
from function import Session, SessionStorage


def test_save_reload_list_delete(tmp_path):
    storage = SessionStorage(tmp_path)
    first = storage.create()
    second = storage.create()
    assert first.session_id != second.session_id
    first.add_message("user", "你好，出个字谜")
    first.add_message("assistant", "一口咬掉牛尾巴（打一字）")
    storage.save(first)
    # 重新创建存储对象，模拟重启后读取。
    restored = SessionStorage(tmp_path)
    assert restored.load(first.session_id).messages == first.messages
    assert restored.list_ids() == sorted([first.session_id, second.session_id], reverse=True)
    assert restored.delete(first.session_id)
    assert not restored.exists(first.session_id)
    assert not restored.delete(first.session_id)
    assert restored.load(first.session_id).messages == []


def test_reads_original_json_format(tmp_path):
    old = {"session_id": "2026-10-30_19-52-39", "messages": [{"role": "user", "content": "猜谜"}]}
    (tmp_path / f"{old['session_id']}.json").write_text(json.dumps(old, ensure_ascii=False), encoding="utf-8")
    assert SessionStorage(tmp_path).load(old["session_id"]).to_dict() == old


def test_failed_write_keeps_previous_record(tmp_path):
    storage = SessionStorage(tmp_path)
    session = storage.create()
    before = (tmp_path / f"{session.session_id}.json").read_bytes()
    session.add_message("user", object())
    with pytest.raises(TypeError):
        storage.save(session)
    assert (tmp_path / f"{session.session_id}.json").read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("unsafe", ["../outside", "..\\outside", "C:\\secret", "/outside", ""])
def test_rejects_paths_outside_sessions(tmp_path, unsafe):
    with pytest.raises(ValueError):
        SessionStorage(tmp_path).save(Session(unsafe))


def test_api_chat_and_history(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SESSIONS_DIR", tmp_path)
    monkeypatch.setattr(config, "DEEPSEEK_API_KEY", "test-key-not-real")
    import main
    from AI_interaction import RiddleAI
    from fastapi.testclient import TestClient

    monkeypatch.setattr(main, "storage", SessionStorage(tmp_path))
    monkeypatch.setattr(main, "ai", RiddleAI(main.storage))
    calls = []

    def reply(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="模拟字谜回复"))])

    monkeypatch.setattr(main.ai.client.chat.completions, "create", reply)
    with TestClient(main.app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/static/app.js").status_code == 200
        created = client.post("/api/sessions").json()
        sid = created["data"]["session_id"]
        assert sid in client.get("/api/sessions").json()["data"]
        for _ in range(2):
            response = client.post("/api/chat", json={"session_id": sid, "message": "再来一题"})
            assert response.json()["data"] == "模拟字谜回复"
        assert len(calls) == 2  # 相同输入也会结合当前历史调用模型。
        assert len(calls[1]["messages"]) == 4  # 系统提示、两条历史消息、本次输入。
        history = client.get(f"/api/sessions/{sid}").json()["data"]
        assert len(history) == 4
        assert SessionStorage(tmp_path).load(sid).messages == history
        assert client.post("/api/chat", json={"message": "缺少编号"}).status_code == 422
        assert client.delete(f"/api/sessions/{sid}").json()["code"] == 200
        assert client.get("/api/sessions").json()["data"] == []
        assert client.delete(f"/api/sessions/{sid}").json()["code"] == 404
