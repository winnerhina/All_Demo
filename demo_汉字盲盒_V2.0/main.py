import logging
import sys
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from function import ApiRequest, ApiResponse, SessionStorage
from AI_interaction import RiddleAI
import db


# 启动时初始化数据库表
db.init_db()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", encoding="utf-8"),
    ],
)

app = FastAPI(title="汉字盲盒")

app.mount("/static", StaticFiles(directory="static"), name="static")


storage = SessionStorage()
ai = RiddleAI(storage)


def get_storage() -> SessionStorage:
    """依赖：返回会话存储对象。"""
    return storage


def get_ai() -> RiddleAI:
    """依赖：返回字谜 AI 助手对象。"""
    return ai


# 依赖注入类型别名
Storage = Annotated[SessionStorage, Depends(get_storage)]
AIDep = Annotated[RiddleAI, Depends(get_ai)]


@app.get("/")
def game_root() -> FileResponse:
    logging.info("用户访问了首页")
    return FileResponse("static/index.html")


@app.post("/api/sessions")
def create_session(storage: Storage) -> ApiResponse:
    logging.info("用户创建了会话")
    session = storage.create()
    return ApiResponse(code=200, message="会话创建成功", data=session.to_dict())


@app.post("/api/chat")
def chat(request: ApiRequest, storage: Storage, ai: AIDep) -> ApiResponse:
    logging.info(f"<------------------ 用户向AI大模型发送了消息：{request.message}")
    session = storage.load(request.session_id)
    reply = ai.chat(session, request.message)
    logging.info(f"------------------> AI大模型回复了：{reply}")
    return ApiResponse(code=200, message="消息发送成功", data=reply)


@app.get("/api/sessions")
def load_sessions(storage: Storage) -> ApiResponse:
    logging.info("加载了会话列表")
    return ApiResponse(code=200, message="会话列表加载成功", data=storage.list_ids())


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, storage: Storage) -> ApiResponse:
    logging.info(f"用户删除了会话：{session_id}")
    if not storage.delete(session_id):
        return ApiResponse(code=404, message="会话数据不存在", data=None)
    return ApiResponse(code=200, message="会话删除成功", data=None)


@app.get("/api/sessions/{session_id}")
def load_messages(session_id: str, storage: Storage) -> ApiResponse:
    logging.info(f"用户加载了会话：{session_id}的历史消息")
    session = storage.load(session_id)
    return ApiResponse(code=200, message="会话历史消息加载成功", data=session.messages)


@app.exception_handler(Exception)
def handle_exception(request, exc):
    logging.error(f"全局异常：{exc}")
    return JSONResponse(status_code=500, content={"code": 500, "message": "服务器内部错误", "data": None})
