import hashlib

import streamlit as st
from openai import OpenAI

import cache
import config
import db
import function


def _reply_cache_key(text):
    """按昵称、性格、用户消息生成 AI 回复缓存键。"""
    raw = f"{st.session_state.nickname}|{st.session_state.personality}|{text}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


# 启动时初始化数据库表
db.init_db()

st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="resources/logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'nickname' not in st.session_state:
    st.session_state.nickname = "夏美子"
if 'personality' not in st.session_state:
    st.session_state.personality = "聪明可爱娇小的女孩"
if 'filename' not in st.session_state:
    st.session_state.filename = function.session_filename()

# 侧边栏
with st.sidebar:
    if st.button("新建会话", width="stretch", icon="🔄"):
        # 当前会话有内容时先保存，再重置为空会话
        if st.session_state.messages:
            function.session_save()
        st.session_state.messages = []
        st.session_state.nickname = "夏美子"
        st.session_state.personality = "聪明可爱娇小的女孩"
        st.session_state.filename = function.session_filename()
        st.rerun()

    st.text("历史会话")
    for s in function.sessions_load():
        col1, col2 = st.columns([4, 1])
        with col1:
            is_current = s == st.session_state.filename
            if st.button(s, width="stretch", icon="📃", key=s,
                         type="primary" if is_current else "secondary"):
                function.session_save()
                function.session_load(s)
                st.rerun()
        with col2:
            if st.button("", width="stretch", icon="❌", key=f"{s}_delete"):
                function.session_delete(s)
                st.rerun()

    st.subheader("定制专属你的AI智能伴侣")
    nickname = st.text_input("请定义AI智能伴侣的昵称：", key="nickname", placeholder="请输入您的昵称")
    personality = st.text_input("请定义AI智能伴侣的性格：", key="personality", placeholder="请输入您的性格")

# 大模型客户端
client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=config.DEEPSEEK_BASE_URL)

# 系统提示词
system_prompt = f"""
# 你叫{st.session_state.nickname}，现在是用户的真实伴侣，请完全代入伴侣角色。
规则：
    1. 每次只回1条消息
    2. 匹配用户的语言
    3. 回复简短，像微信聊天一样
    4. 有需要的话可以用❤️🌸等emoji表情
    5. 用符合伴侣性格的方式对话
    6. 回复的内容，要充分体现伴侣的性格特征
    7. 聊天时候可以展示出内心活动
伴侣性格：
    - {st.session_state.personality}
你必须严格遵守上述规则来回复用户。
"""

st.logo("resources/logo.png")
st.title("AI智能伴侣")
st.text(f"当前会话：{st.session_state.filename}")

# 输出聊天历史
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

input_text = st.chat_input("请输入您要和AI智能伴侣的互动内容：")
if input_text:
    st.chat_message("user").write(input_text)
    st.session_state.messages.append({"role": "user", "content": input_text})

    msg_hash = _reply_cache_key(input_text)
    cached_reply = cache.get_cached_ai_reply(msg_hash)

    if cached_reply is not None:
        # 命中缓存，直接复用，不重复调用大模型
        st.chat_message("assistant").write(cached_reply)
        st.session_state.messages.append({"role": "assistant", "content": cached_reply})
    else:
        try:
            response = client.chat.completions.create(
                model=config.DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *st.session_state.messages,
                ],
                stream=True,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}}
            )

            with st.chat_message("assistant"):
                response_message = st.empty()
                content = ""
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content is not None:
                        content += chunk.choices[0].delta.content
                        response_message.write(content)
            st.session_state.messages.append({"role": "assistant", "content": content})
            cache.cache_ai_reply(msg_hash, content)
        except Exception as e:
            st.error(f"调用大模型失败：{e}")

    # 每次互动后保存会话，并刷新页面同步会话列表
    function.session_save()
    st.rerun()
