from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import sys
from typing import Annotated
# typing：类型提示库，用于在代码中添加类型信息，帮助 IDE 和工具理解代码
# sys：标准库，提供系统级的函数和变量，如标准输入输出、环境变量等

from function import ApiRequest, ApiResponse, SessionStorage
from AI_interaction import RiddleAI


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到控制台
        logging.FileHandler("app.log", encoding="utf-8"),  # 同时写入 app.log
    ],
)

# 创建 FastAPI 实例
app = FastAPI(title="汉字盲盒")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# 创建实例对象
storage = SessionStorage()  
ai = RiddleAI(storage)

#  创建依赖注入
def get_storage() -> SessionStorage:
    """依赖：返回会话存储对象"""
    return storage

def get_ai() -> RiddleAI:
    """依赖：返回字谜 AI 助手对象"""
    return ai


# 创建类型别名
""" 
    变量 = Annotated[类型(变量), 附加信息(依赖注入)]
    annotated 在python内，只有第一个参数生效，其他参数仅仅只是附加信息。
    在其他类型的标签中，那annotated内那个参数能被认识，那个参数就有效
    例如在FastAPI标签下，能够识别Depends函数，自动注入依赖对象
"""
Storage = Annotated[SessionStorage, Depends(get_storage)]
AIDep = Annotated[RiddleAI, Depends(get_ai)]



# 首页路由
@app.get("/")
def game_root() -> FileResponse:
    logging.info("用户访问了首页")
    return FileResponse("static/index.html")


# 新建会话路由
@app.post("/api/sessions")
def create_session(storage: Storage) -> ApiResponse:
    logging.info("用户创建了会话")
    session = storage.create()
    return ApiResponse(code=200, message="会话创建成功", data=session.to_dict())


# 聊天路由
@app.post("/api/chat")
def chat(request: ApiRequest, storage: Storage, ai: AIDep) -> ApiResponse:
    logging.info(f"<------------------ 用户向AI大模型发送了消息：{request.message}")
    session = storage.load(request.session_id)
    reply = ai.chat(session, request.message)
    logging.info(f"------------------> AI大模型回复了：{reply}")
    return ApiResponse(code=200, message="消息发送成功", data=reply)


# 加载会话列表路由
@app.get("/api/sessions")
def load_sessions(storage: Storage) -> ApiResponse:
    logging.info("加载了会话列表")
    return ApiResponse(code=200, message="会话列表加载成功", data=storage.list_ids())


# 删除会话路由
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, storage: Storage) -> ApiResponse:
    logging.info(f"用户删除了会话：{session_id}")
    if not storage.delete(session_id):
        return ApiResponse(code=404, message="会话数据不存在", data=None)
    return ApiResponse(code=200, message="会话删除成功", data=None)


# 加载历史消息路由
@app.get("/api/sessions/{session_id}")
def load_messages(session_id: str, storage: Storage) -> ApiResponse:
    logging.info(f"用户加载了会话：{session_id}的历史消息")
    session = storage.load(session_id)
    return ApiResponse(code=200, message="会话历史消息加载成功", data=session.messages)


# 全局异常捕获路由
@app.exception_handler(Exception)
def handle_exception(request, exc):
    logging.error(f"全局异常：{exc}")
    # 异常处理器必须返回 Response 对象（JSONResponse），返回 Pydantic 模型会变成纯文本 500
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误", "data": None})


