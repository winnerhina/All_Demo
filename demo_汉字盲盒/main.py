from fastapi.responses import FileResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import json
import logging


import function
import AI_interaction



# 配置日志记录
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )



# 创建FastAPI实例
app = FastAPI(title="汉字盲盒")

# 配置静态文件目录
# 任何以"/static"开头的；路由请求都从"static"目录中查找对应的文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 保存会话数据到本地sessions目录
if not os.path.exists("sessions"):
    os.makedirs("sessions")

# 创建路径操作函数
@app.get("/")
def root():
    logging.info("访问项目首页")
    return FileResponse("static/index.html")

# 创建新建会话路由
@app.post("/api/sessions")
def create_session() -> function.ApiResponse:
    logging.info("创建新会话")
    # 1.生成会话ID
    session_id = function.create_session_id()

    # 2.构造会话数据，并保存到sessions目录
    session_data = {
        "session_id": session_id,
        "messages": []
    }
    with open(f"sessions/{session_id}.json", "w") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=4)

    # 3.返回响应数据(封装为对象)
    return function.ApiResponse(code=200, message="会话创建成功", date=session_id)

# 创建聊天路由
@app.post("/api/chat")
def chat(request:function.ApiRequest) -> function.ApiResponse:
    logging.info(f"<-----------------与AI互动：{request.session_id} : {request.message}")

    # 逻辑实现
    messages = AI_interaction.get_ai_response(request.session_id, request.message)

    # 7.给前端响应数据
    return function.ApiResponse(code=200, message="聊天成功", date=messages)

# 创建加载历史会话列表功能
@app.get("/api/sessions")
def load_sessions() -> function.ApiResponse:
    logging.info("加载历史会话列表")
    # 1.获取所有会话文件名
    session_files = os.listdir("sessions")
    # 2.去掉文件扩展名
    session_files = [file.split(".")[0] for file in session_files]
    # 3.根据会话ID排序
    session_files.sort(reverse=True)
    # 4.返回响应数据(封装为对象)
    return function.ApiResponse(code=200, message="会话列表加载成功", date=session_files)

# 创建加载历史会话消息路由
@app.get("/api/sessions/{session_id}")
def load_session_messages(session_id: str) -> function.ApiResponse:
    logging.info(f"加载会话消息：{session_id}")
    # 1.获取会话数据
    with open(f"sessions/{session_id}.json", "r",encoding="utf-8") as f:
        session_data = json.load(f)
    # 2.返回响应数据(封装为对象)
    return function.ApiResponse(code=200, message="会话消息加载成功", date=session_data["messages"])

# 创建删除会话路由
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str) -> function.ApiResponse:
    logging.info(f"删除会话：{session_id}")
    # 1.删除会话文件
    if os.path.exists(f"sessions/{session_id}.json"):
        os.remove(f"sessions/{session_id}.json")
    # 2.返回响应数据(封装为对象)
    return function.ApiResponse(code=200, message="会话删除成功", date=None)

# 创建捕获全局异常处理函数
@app.exception_handler(Exception)
def handle_exception(request, exc):
    logging.error(f"异常的请求{request.url}异常信息·：{exc}")
    return function.ApiResponse(code=500, message="服务器内部错误", date=None)



# 运行FastAPI应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # access_log=False关闭日志
