# 汉字盲盒 V2.0

一个基于 **FastAPI + DeepSeek 大模型**的猜字谜 Web 应用。用户通过浏览器与 AI 助手互动猜字谜，支持多会话管理、历史消息回顾。

## 功能特性

- 🎯 **AI 出题**：调用 DeepSeek 大模型随机出字谜，并避免重复老题
- ✅ **智能判题**：识别模糊表述（如「江」「jianɡ」都能判对），答对/答错差异化反馈
- 💬 **多会话管理**：新建、删除、切换会话
- 🕐 **历史回顾**：加载任意会话的历史消息
- 📝 **本地持久化**：会话数据以 JSON 文件形式保存在本地

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| AI 大模型 | DeepSeek（OpenAI SDK 调用） |
| 数据校验 | Pydantic |
| 前端 | 原生 HTML / CSS / JavaScript |
| 数据存储 | 本地 JSON 文件（sessions/ 目录） |

## 目录结构

```
demo_汉字盲盒_V2.0/
├── main.py             # FastAPI 应用入口，路由与依赖注入
├── AI_interaction.py   # RiddleAI 类：封装 DeepSeek 调用与提示词
├── function.py         # 数据模型与会话存储（ApiRequest/ApiResponse/Session/SessionStorage）
├── static/             # 前端静态资源
│   ├── index.html       # 页面结构
│   ├── style.css        # 样式
│   └── app.js           # 前端交互逻辑
├── sessions/           # 会话数据目录（本地聊天记录，自动生成）
└── app.log             # 运行日志（自动生成）
```

## 环境要求

- Python 3.11+
- DeepSeek API Key

## 安装与运行

1. 安装依赖：

```bash
pip install fastapi uvicorn openai pydantic
```

2. 配置环境变量（DeepSeek API Key）：

```bash
# Windows (PowerShell)
$env:DEEPSEEK_API_KEY_1="你的 API Key"

# macOS / Linux
export DEEPSEEK_API_KEY_1="你的 API Key"
```

3. 启动服务：

```bash
uvicorn main:app --reload
```

4. 浏览器打开 http://127.0.0.1:8000 开始猜字谜。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 返回首页页面 |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions` | 获取会话 ID 列表 |
| DELETE | `/api/sessions/{session_id}` | 删除指定会话 |
| GET | `/api/sessions/{session_id}` | 加载会话历史消息 |
| POST | `/api/chat` | 发送消息，AI 判题并回复 |

## 关于 AI 提示词

系统提示词位于 [AI_interaction.py](AI_interaction.py) 中的 `SYSTEM_PROMPT`，约束 AI 只进行字谜互动、不闲聊无关内容，并包含出题、判题、互动流程等规则。