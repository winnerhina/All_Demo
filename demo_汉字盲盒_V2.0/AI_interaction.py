"""字谜 AI 助手：封装 DeepSeek 调用与会话历史维护。"""
import hashlib

from openai import OpenAI

import cache
import config
from function import Session, SessionStorage


# 系统提示词：约束 AI 只做字谜互动
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
5. 用户回答不知道的时候，要提示用户继续思考，不要直接回答，要是用户再次回答不知道，要给答案，并鼓励用户。

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


class RiddleAI:
    """字谜 AI 助手：封装大模型调用与会话历史维护。"""

    def __init__(self, storage: SessionStorage, system_prompt: str = SYSTEM_PROMPT):
        self.storage = storage
        self.system_prompt = system_prompt
        self.client = OpenAI(
            api_key=config.DEEPSEEK_API_KEY,
            base_url=config.DEEPSEEK_BASE_URL,
        )

    def _reply_cache_key(self, session_id: str, user_message: str) -> str:
        """按会话与用户消息生成 AI 回复缓存键。"""
        return hashlib.md5(f"{session_id}|{user_message}".encode("utf-8")).hexdigest()

    def chat(self, session: Session, user_message: str) -> str:
        """对话：命中缓存直接复用，未命中调用大模型并回填缓存。"""
        msg_hash = self._reply_cache_key(session.session_id, user_message)
        cached_reply = cache.get_cached_ai_reply(msg_hash)
        if cached_reply is not None:
            session.add_message("user", user_message)
            session.add_message("assistant", cached_reply)
            self.storage.save(session)
            return cached_reply

        # 组装消息：系统提示 + 会话历史 + 本次用户消息
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(session.messages)
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=config.DEEPSEEK_MODEL,
            messages=messages,
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}},
        )
        reply = response.choices[0].message.content

        session.add_message("user", user_message)
        session.add_message("assistant", reply)
        self.storage.save(session)

        cache.cache_ai_reply(msg_hash, reply)
        return reply
