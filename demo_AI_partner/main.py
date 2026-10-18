import streamlit as st
import os
from openai import OpenAI
import function

# 日志
print("-------------->开始运行AI智能伴侣：\n")

# 设置页面的配置
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="resources/logo.png",
    # 布局
    layout="wide",
    # 控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)

# 初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []
# 初始化昵称和性格
if 'nickname' not in st.session_state:
    st.session_state.nickname = "夏美子"
if 'personality' not in st.session_state:
    st.session_state.personality = "聪明可爱娇小的女孩"
if 'filename' not in st.session_state:
    st.session_state.filename = function.session_filename()


# 设置侧边栏 - with:streamlit里面的上下文管理器
with st.sidebar:
    # 新建会话
    if st.button("新建会话",width="stretch",icon="🔄"):
        # 1. 如果当前会话有聊天记录，先保存，避免丢失
        if st.session_state.messages:
            function.session_save()
        # 2. 无论当前是否为空，都重置为一个全新的空会话（保证按钮始终有反应）
        st.session_state.messages = []
        st.session_state.nickname = "夏美子"
        st.session_state.personality = "聪明可爱娇小的女孩"
        st.session_state.filename = function.session_filename()
        # 3. 重新加载页面（新会话先不保存，等第一次聊天后再自动保存，避免历史列表出现空白记录）
        st.rerun()
        
    # 加载历史会话
    st.text("历史会话")
    session_list = function.sessions_load()
    for s in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            # 三元运算符：根据是否是当前会话，判断按钮的类型
            # 三元运算符格式：值1 if 条件 else 值2
            if st.button(s,width="stretch",icon="📃",key=s,type="primary" if s==st.session_state.filename else "secondary"):
                # 切换前先保存当前会话，防止当前聊了一半的内容丢失
                function.session_save()
                function.session_load(s)
                st.rerun()
        with col2:
            if st.button("",width="stretch",icon="❌",key=f"{s}_delete"):
                function.session_delete(s)
                st.rerun()


    st.subheader("定制专属你的AI智能伴侣")
    # 昵称输入框（通过key直接绑定session_state，输入时自动同步，无需手动赋值回写）
    nickname = st.text_input("请定义AI智能伴侣的昵称：", key="nickname", placeholder="请输入您的昵称")
    # 性格输入框
    personality = st.text_input("请定义AI智能伴侣的性格：", key="personality", placeholder="请输入您的性格")



# 调用大模型进行交互
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_1'),base_url="https://api.deepseek.com")

# 系统提示词
system_prompt = f"""
# 你叫{nickname}，现在是用户的真实伴侣，请完全代入伴侣角色。
规则：
    1. 每次只回1条消息
    2. 匹配用户的语言
    3. 回复简短，像微信聊天一样
    4. 有需要的话可以用❤️🌸等emoji表情
    5. 用符合伴侣性格的方式对话
    6. 回复的内容，要充分体现伴侣的性格特征
    7. 聊天时候可以展示出内心活动
伴侣性格：
    - {personality}
你必须严格遵守上述规则来回复用户。
"""

# 导入logo
st.logo("resources/logo.png")

# 大标题
st.title("AI智能伴侣")
# 输出当前会话信息
st.text(f"当前会话：{st.session_state.filename}")

# 输出聊天历史
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 聊天输入框
input_text = st.chat_input("请输入您要和AI智能伴侣的互动内容：")
if input_text:
    st.chat_message("user").write(input_text)
    # 记录用户输入
    st.session_state.messages.append({"role": "user", "content": input_text})
    # 日志
    print("-------------->调用ai大模型：\n", input_text)

    # 与ai大模型进行交互
    print(st.session_state.messages)  # 日志

    # 输出大模型返回的结果（非流失输出
    # print("<-------------大模型返回的结果：\n", response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 与大模型交互可能出现网络错误、接口报错等异常，用try捕获，出错时给出提示，避免整个页面崩溃
    try:
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                # 解包聊天历史，使得大模型拥有记忆功能。
                *st.session_state.messages,
            ],
            stream=True,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}}
        )

        # 输出大模型返回的结果（流失输出）
        with st.chat_message("assistant"):
            response_message = st.empty()  # 占位符：放在气泡内，用于实时更新气泡内容
            content = ""
            for chunk in response:
                # 先判断chunk.choices非空（个别数据块可能没有choices内容），防止IndexError
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    content += chunk.choices[0].delta.content
                    response_message.write(content)
        # 记录大模型返回的结果
        st.session_state.messages.append({"role": "assistant", "content": content})
    except Exception as e:
        st.error(f"调用大模型失败：{e}")

    # 保存当前会话信息--每完成一次互动，就保存一次会话信息
    function.session_save()
    # 刷新页面，显示最新的聊天记录并同步左侧会话列表
    st.rerun()