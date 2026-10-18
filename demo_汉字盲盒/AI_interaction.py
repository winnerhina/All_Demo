import function
import os
from openai import OpenAI
import logging

# 系统提示词

SYSTEM_PROMPT = """
你是一个专门玩猜字谜的AI小助手，只进行字谜互动，不闲聊与字谜无关的内容。

一、出题规则
1. 每次给用户出一个字谜，格式固定为："谜面"（打一字），例如：一口咬掉牛尾巴（打一字）。
2. 出题时避开已经出过的谜语，避免使用高频重复的经典老谜语。
3. 主动记录已经使用过的谜语，避免和其它会话/题目重复。
4. 挑选常见、难度适中的谜语，不生僻、不低俗、不使用网络烂梗。

二、判题规则（最重要！）
1. 判断用户答案时，要能识别模糊表述。例如：
   - 用户说"江字""江""jiang" → 都解析为「江」
   - 用户说"是江吗？""应该是江" → 同样解析为「江」
2. 答对时，用欢快语气反馈，模板："太棒了！答对了！就是'XX'字！要不要再来一题？"
3. 答错时，不要直接批评，模板："不对哦，再想想~ 给你个小提示：[简短线索，不泄露答案]"
4. 提示只能给线索，严禁泄露答案。

三、互动流程
1. 开场先主动出一个谜语，引导用户来猜。
2. 用户猜对后，询问是否继续；继续则出新题，不继续则适当结束并告别。
3. 整个过程保持轻松、鼓励、有趣的语气。

四、其他要求
1. 语气轻松有趣、简洁明快，不啰嗦。
2. 全程只围绕字谜，不回答其他问题、不聊无关话题。
3. 不使用多余表情符号，保持简洁。
4. 若用户答案与正确答案仅差一字或笔画，请仔细核对是否正确。

请严格按以上规则回复，优先保证谜语的随机性和多样性。
"""

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )

# 调用大模型进行交互
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY_1'),base_url="https://api.deepseek.com")

# AI交互主要功能以及保存会话信息，最终返回个前端的响应数据
def get_ai_response(session_id: str, message: str) -> list:
    """
    与AI互动，获取AI回复。
    :param session_id: 会话ID
    :param message: 用户消息
    :return: 包含用户消息和AI回复的消息列表
    """
    # 1.加载json中的会话数据
    session_data = function.load_session_data(session_id)

    # 2.构建AI大模型交互的消息数据
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in session_data["messages"]:
        messages.append(msg)
    messages.append({"role": "user", "content": message})

    # 3.调用大模型
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages = messages,
        stream=False,
        temperature=1.5,    # 模型输出的随机性，多样性，创造性
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    
    # 4.获取响应数据
    new_message = response.choices[0].message.content
    logging.info(f"------------------>AI大模型的响应：{new_message}")

    # 5.更新消息列表中信息
    messages.pop(0)
    session_data["messages"].append({"role": "assistant", "content": new_message})
    logging.info(f"更新后的消息列表：{session_data['messages']}")

    # 6.保存会话数据到sessions目录
    function.save_session_data(session_id, session_data)

    return new_message




