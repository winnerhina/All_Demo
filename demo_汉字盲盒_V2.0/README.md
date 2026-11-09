# 汉字盲盒 V2.0

一个基于 Python、FastAPI 和 DeepSeek API 的猜字谜应用。用户可以在网页上与 AI 互动，并管理不同的聊天会话。聊天记录保存到本地 JSON 文件。

## 功能

- 调用大模型出字谜，并根据用户的回答继续互动。
- 新建、查看、切换和删除会话。
- 保存与读取历史聊天记录。
- 使用 Pydantic 检查请求参数，记录运行与错误日志。

## 本地运行

需要 Python 3.11 或更新版本。先进入本项目文件夹，再执行：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

在本地 `.env` 中填写 `DEEPSEEK_API_KEY_1`，然后使用下面的启动命令。密钥不要写进代码或提交到 GitHub。

```powershell
python -m uvicorn main:app --reload
```

浏览器打开 `http://127.0.0.1:8000`。

## 聊天记录保存在哪里

- 默认保存在本项目的 `sessions/` 文件夹，一个会话对应一个 `.json` 文件。
- 发送消息后自动保存；重启后可以从历史列表继续聊天。
- 原来相同格式的 JSON 记录可以直接读取，不需要转换。
- 先写临时文件，写完再替换正式文件，避免写入失败损坏已有记录。
- 删除会话会删除对应的本地 JSON 文件。
- `sessions/` 与 `.env` 已加入本项目的 `.gitignore`，不会随代码提交。

## 配置项

| 环境变量 | 作用 | 默认值 |
|---|---|---|
| `DEEPSEEK_API_KEY_1` | 大模型接口密钥 | 必填 |
| `DEEPSEEK_BASE_URL` | 大模型接口地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称，可按账号支持的模型调整 | `deepseek-flash` |
| `SESSIONS_DIR` | 聊天记录保存目录 | `sessions` |

`SESSIONS_DIR` 的相对路径以本项目目录为起点，也可以使用绝对路径。

## 检查功能

```powershell
python -m pip install pytest httpx
python -m pytest tests -q
```

测试使用临时文件和模拟模型回复，不会读取你的聊天记录，也不会调用付费模型接口。

## 每个文件的作用

| 文件 | 作用 |
|---|---|
| `main.py` | FastAPI 入口，提供首页和 5 个业务接口，处理异常并记录日志 |
| `function.py` | 定义请求、响应和会话对象；创建、保存、读取、删除本地 JSON 会话 |
| `AI_interaction.py` | 保存字谜提示词，调用模型，把用户与 AI 的消息加入历史记录 |
| `config.py` | 读取模型配置和聊天记录目录 |
| `.env.example` | 不含真实密钥的配置示例 |
| `requirements.txt` | 运行项目所需的 Python 库 |
| `.gitignore` | 避免提交聊天记录、密钥、日志和临时文件 |
| `static/index.html` | 网页结构 |
| `static/style.css` | 页面样式 |
| `static/app.js` | 调用后端接口，更新聊天界面和会话列表 |
| `tests/test_json_storage.py` | 检查 JSON 保存恢复、旧格式兼容、写入失败保护和接口流程 |
| `README.md` | 项目说明、运行步骤和文件用途 |

## 接口

| 方法 | 路径 | 功能 |
|---|---|---|
| GET | `/` | 首页 |
| POST | `/api/sessions` | 创建会话 |
| GET | `/api/sessions` | 查看会话列表 |
| GET | `/api/sessions/{session_id}` | 读取历史消息 |
| DELETE | `/api/sessions/{session_id}` | 删除会话 |
| POST | `/api/chat` | 发送消息并获取 AI 回复 |
