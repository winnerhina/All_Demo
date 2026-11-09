"""验证 JSON 存储与 Streamlit 聊天页面；不调用真实模型。"""
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import config
import function


@pytest.fixture
def state(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SESSIONS_DIR", tmp_path)
    state = SimpleNamespace(filename="2026-10-04-172129", nickname="小伙伴", personality="开朗",
                            messages=[{"role": "user", "content": "你好"}])
    monkeypatch.setattr(function, "st", SimpleNamespace(session_state=state, toast=lambda *a, **kw: None))
    return state


def test_save_restore_delete(state, tmp_path):
    function.session_save()
    assert function.sessions_load() == [state.filename]
    saved = json.loads((tmp_path / f"{state.filename}.json").read_text(encoding="utf-8"))
    assert saved == vars(state)
    filename = state.filename
    state.messages = []
    state.nickname = "修改后的临时昵称"
    function.session_load(filename)
    assert state.nickname == "小伙伴"
    assert state.messages == saved["messages"]
    function.session_delete(filename)
    assert function.sessions_load() == []
    assert state.messages == []
    assert state.filename != filename


def test_old_json_and_empty_conversation(state, tmp_path):
    old = {"filename": "2026-10-04-172157", "nickname": "旧昵称", "personality": "温和",
           "messages": [{"role": "assistant", "content": "你好"}]}
    (tmp_path / (old["filename"] + ".json")).write_text(json.dumps(old), encoding="utf-8")
    function.session_load(old["filename"])
    assert vars(state) == old
    state.filename = "empty"
    state.messages = []
    function.session_save()
    assert not (tmp_path / "empty.json").exists()


def test_failed_write_keeps_previous_record(state, tmp_path):
    function.session_save()
    path = tmp_path / (state.filename + ".json")
    before = path.read_bytes()
    state.messages.append(object())
    with pytest.raises(TypeError):
        function.session_save()
    assert path.read_bytes() == before
    assert not list(tmp_path.glob("*.tmp"))


@pytest.mark.parametrize("unsafe", ["../outside", "..\\outside", "C:\\secret", "/outside", ""])
def test_rejects_paths_outside_sessions(state, unsafe):
    with pytest.raises(ValueError):
        function._session_path(unsafe)


def test_streamlit_chat_switch_and_delete(tmp_path, monkeypatch):
    import openai
    from streamlit.testing.v1 import AppTest

    monkeypatch.setattr(config, "SESSIONS_DIR", tmp_path)
    calls = []

    def completion(**kwargs):
        calls.append(kwargs)
        return iter([SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=piece))])
                     for piece in ["你好，", "我是模拟回复。"]])

    monkeypatch.setattr(openai, "OpenAI", lambda **kw: SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=completion))))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "main.py"), default_timeout=20).run()
    assert not app.exception
    app.text_input(key="nickname").set_value("测试角色").run()
    app.text_input(key="personality").set_value("开朗").run()
    app.chat_input[0].set_value("你好").run()
    assert not app.exception
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    saved = json.loads(files[0].read_text(encoding="utf-8"))
    sid = saved["filename"]
    assert saved["nickname"] == "测试角色"
    assert saved["messages"][-1]["content"] == "你好，我是模拟回复。"
    app.button[0].click().run()  # 新建会话
    assert not app.exception
    app.button(key=sid).click().run()  # 恢复刚保存的会话
    assert app.session_state["nickname"] == "测试角色"
    assert app.session_state["messages"] == saved["messages"]
    app.chat_input[0].set_value("你好").run()
    assert len(calls) == 2
    assert len(calls[1]["messages"]) == 4
    app.button(key=f"{sid}_delete").click().run()
    assert not app.exception
    assert not list(tmp_path.glob("*.json"))
    assert app.session_state["messages"] == []
