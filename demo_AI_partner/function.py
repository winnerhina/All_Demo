import streamlit as st
import os
import json
import datetime
import streamlit as st
# 保存会话信息函数
def session_save():
    # 构建保存的当前会话的json格式
    session_json = {
        "nickname": st.session_state.nickname,
        "personality": st.session_state.personality,
        "filename": st.session_state.filename,
        "messages": st.session_state.messages
    }
    
    # 会话中没有任何聊天记录时不保存，避免产生空白的历史会话文件
    if st.session_state.filename and st.session_state.messages:
        # 如果sessions目录不存在，创建它
        if not os.path.exists("sessions"):
            os.makedirs("sessions")
        # 保存当前会话
        with open(f"sessions/{st.session_state.filename}.json", "w",encoding="utf-8") as f:
            json.dump(session_json, f, ensure_ascii=False, indent=4)

# 定义要保存的会话名称
def session_filename():
    return f"{datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

# 加载历史会话框信息函数
def sessions_load():
    session_list = []
    # 加载sessions目录下的所有文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        # 收集所有json文件
        for file in file_list:
            if file.endswith(".json"):
                file = file[:-5]
                session_list.append(file)
        session_list.sort(reverse=True)
    return session_list

# 加载会话信息函数
def session_load(s_file):
    try:
        if os.path.exists(f"sessions/{s_file}.json"):
            with open(f"sessions/{s_file}.json", "r",encoding="utf-8") as f:
                session_json = json.load(f)
                st.session_state.nickname = session_json["nickname"]
                st.session_state.personality = session_json["personality"]
                # 直接用s_file作为会话文件名，不使用json里保存的filename
                # （旧版本保存的filename带.json后缀，会导致下次保存时生成"xxx.json.json"文件）
                st.session_state.filename = s_file
                st.session_state.messages = session_json["messages"]
    except Exception as e:
        st.toast(f"加载会话信息失败：{e}", icon="⚠️")

# 删除会话信息函数
def session_delete(s_file):
    try:
        # 会话文件存在才删除（当前会话可能刚新建、还没保存成文件）
        if os.path.exists(f"sessions/{s_file}.json"):
            os.remove(f"sessions/{s_file}.json")
        st.toast(f"会话{s_file}已删除", icon="🗑️")
        # 删除的是当前会话时，无论文件是否存在，都要重置为一个全新的空会话
        if s_file == st.session_state.filename:
            st.session_state.filename = session_filename()
            st.session_state.nickname = "夏美子"
            st.session_state.personality = "聪明可爱娇小的女孩"
            st.session_state.messages = []
    except Exception as e:
        st.toast(f"删除会话{s_file}失败：{e}", icon="⚠️")