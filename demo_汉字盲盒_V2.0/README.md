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
```

在同一个 PowerShell 窗口中设置自己的模型密钥：

```powershell
$env:DEEPSEEK_API_KEY_1 = '填写你自己的DeepSeek密钥'
```

这个设置只对当前终端及其启动的程序生效。新开终端时需要重新设置；不要把真实密钥写进源代码。然后执行启动命令：

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
- `sessions/` 是运行后生成的本地数据，不属于仓库文件。上传代码时请将它加入本地 Git 忽略规则。

## 配置项

| 环境变量 | 作用 | 默认值 |
|---|---|---|
| `DEEPSEEK_API_KEY_1` | 大模型接口密钥 | 必填 |
| `DEEPSEEK_BASE_URL` | 大模型接口地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | 模型名称，可按账号支持的模型调整 | `deepseek-flash` |
| `SESSIONS_DIR` | 聊天记录保存目录 | `sessions` |

`SESSIONS_DIR` 的相对路径以本项目目录为起点，也可以使用绝对路径。

`config.py` 也支持读取自己创建的本地 `.env` 文件；如使用这种方式，请将 `.env` 加入本地 Git 忽略规则。仓库不包含密钥文件。

## 使用检查

启动后，新建会话并发送消息；关闭程序后重新启动，从历史列表打开刚才的会话，检查消息是否保存。删除会话后，对应 JSON 文件也会删除。

## 每个文件的作用

| 文件 | 作用 |
|---|---|
| `main.py` | FastAPI 入口，提供首页和 5 个业务接口，处理异常并记录日志 |
| `function.py` | 定义请求、响应和会话对象；创建、保存、读取、删除本地 JSON 会话 |
| `AI_interaction.py` | 保存字谜提示词，调用模型，把用户与 AI 的消息加入历史记录 |
| `config.py` | 读取模型配置和聊天记录目录 |
| `requirements.txt` | 运行项目所需的 Python 库 |
| `static/index.html` | 网页结构 |
| `static/style.css` | 页面样式 |
| `static/app.js` | 调用后端接口，更新聊天界面和会话列表 |
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
