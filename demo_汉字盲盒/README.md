# 汉字盲盒

一个基于 FastAPI + DeepSeek 的 AI 猜字谜小项目。AI 出谜面，用户猜字，支持多会话、历史记录保存与删除。

## 功能

- 每次会话由 AI 主动出一个字谜（打一字），用户来猜
- 答对给予欢快反馈，答错给出线索提示（不泄露答案）
- 支持创建多个会话，历史消息保存在本地 `sessions` 目录
- 支持加载历史会话列表、查看历史消息、删除会话
- 统一的 JSON 响应格式（`{code, message, date}`）与全局异常处理

## 技术栈

- **FastAPI**：Web 框架，提供 RESTful 接口
- **pydantic**：请求参数与响应数据的校验与封装
- **DeepSeek API**：大模型推理（猜字谜互动）
- **原生 HTML/CSS/JS**：前端页面（`static` 目录）

## 快速开始

### 1. 配置 API Key（重要）

项目通过环境变量读取 API Key，请先设置：

```powershell
# Windows PowerShell
$env:DEEPSEEK_API_KEY_1 = "你的DeepSeek密钥"
```

```bash
# macOS / Linux
export DEEPSEEK_API_KEY_1="你的DeepSeek密钥"
```

> 安全提醒：不要把密钥硬编码进代码，也不要提交 `.env` 文件（已在 `.gitignore` 中忽略）。

### 2. 安装依赖

```bash
pip install fastapi uvicorn openai
```

### 3. 启动服务

```bash
python main.py
```

服务启动后访问：<http://localhost:8000>

## 接口说明

| 方法   | 路径                      | 说明                 |
| ------ | ------------------------- | -------------------- |
| GET    | `/`                       | 返回前端页面         |
| POST   | `/api/sessions`           | 创建新会话           |
| GET    | `/api/sessions`           | 获取历史会话列表     |
| GET    | `/api/sessions/{id}`      | 获取某会话的历史消息 |
| POST   | `/api/chat`               | 发送消息与 AI 互动   |
| DELETE | `/api/sessions/{id}`      | 删除某会话           |

## 项目结构

```
demo_汉字盲盒/
├── main.py            # FastAPI 入口，路由定义
├── function.py        # 响应/请求封装、会话文件读写等工具函数
├── AI_interaction.py  # 调用 DeepSeek 大模型、系统提示词、会话消息管理
├── static/            # 前端静态资源（HTML/CSS/JS）
│   ├── index.html
│   ├── style.css
│   └── app.js
├── sessions/          # 本地聊天记录（JSON，已加入 .gitignore，不会提交）
├── 知识点.text        # 学习笔记
├── .gitignore         # 忽略敏感文件、聊天数据、缓存等
└── README.md          # 本说明文件
```

## 注意事项

- 会话 JSON 文件存放在 `sessions/` 目录，包含聊天内容（个人信息），已通过 `.gitignore` 忽略，不会提交到版本库。
- 启动时会自动创建 `sessions` 目录。
- 聊天数据仅保存在本地，请勿将 `sessions/` 目录内的文件分享或提交。
