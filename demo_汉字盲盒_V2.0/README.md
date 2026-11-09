# 汉字盲盒 V2.0

一个基于 **FastAPI + DeepSeek 大模型** 的猜字谜 Web 应用。用户通过浏览器与 AI 助手互动猜字谜，支持多会话管理、历史消息回顾。

本项目面向初学者，在基础猜字谜功能之上，额外加入了 **SQLite（本地数据库）**、**Redis（缓存）** 和 **Docker（容器化部署）**。

## 功能特性

- 🎯 **AI 出题**：调用 DeepSeek 大模型随机出字谜，并避免重复老题
- ✅ **智能判题**：识别模糊表述（如「江」「jianɡ」都能判对），答对/答错差异化反馈
- 💬 **多会话管理**：新建、删除、切换会话
- 🕐 **历史回顾**：加载任意会话的历史消息
- 💾 **自动保存**：会话数据持久化到 **SQLite**，重启不丢失
- ⚡ **Redis 缓存加速**：会话读缓存、AI 回复缓存，命中后不再重复调用大模型
- 🐳 **Docker 一键部署**：`docker compose up` 启动应用 + Redis

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| AI 大模型 | DeepSeek（OpenAI SDK 调用） |
| 数据校验 | Pydantic |
| 前端 | 原生 HTML / CSS / JavaScript |
| 数据存储 | SQLite（Python 内置，零配置） |
| 缓存 | Redis 7 |
| 部署 | Docker |

## 目录结构

```
demo_汉字盲盒_V2.0/
├── main.py             # FastAPI 应用入口，路由与依赖注入
├── AI_interaction.py   # RiddleAI 类：封装 DeepSeek 调用与 AI 回复缓存
├── function.py         # 数据模型与会话存储（ApiRequest/ApiResponse/Session/SessionStorage）
├── db.py               # SQLite 封装（建表 + 会话增删改查）
├── cache.py            # Redis 缓存封装（会话缓存 + AI 回复缓存）
├── config.py           # 集中配置（从环境变量/.env 读取连接信息）
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例（复制为 .env 后填写）
├── Dockerfile          # 应用镜像构建文件
├── docker-compose.yml  # 一键编排 app + Redis
├── data/               # SQLite 数据库文件目录（运行时生成，已忽略）
└── static/             # 前端静态资源
    ├── index.html      # 页面结构
    ├── style.css       # 样式
    └── app.js          # 前端交互逻辑
```

## 环境要求

- Python 3.11+
- DeepSeek API Key

## 快速开始

### 方式一：Docker 一键启动（推荐初学者）

需要先安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

```bash
cd demo_汉字盲盒_V2.0

# 1. 准备密钥
cp .env.example .env     # Windows 用 copy .env.example .env

# 2. 构建并启动（应用 + Redis）
docker compose up --build

# 3. 停止
docker compose down
```

浏览器打开 `http://localhost:8000`。

### 方式二：本地运行

SQLite 内置无需安装；Redis 需要单独准备（本机安装，或 `docker run -d -p 6379:6379 redis:7-alpine`）。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（复制 .env.example 为 .env 并填写 DEEPSEEK_API_KEY_1）

# 3. 启动服务
uvicorn main:app --reload
```

浏览器打开 `http://127.0.0.1:8000`。

> Redis 连不上会自动降级（跳过缓存继续运行）；SQLite 会自动在 `data/` 目录创建数据库文件。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 返回首页页面 |
| POST | `/api/sessions` | 新建会话 |
| GET | `/api/sessions` | 获取会话 ID 列表 |
| DELETE | `/api/sessions/{session_id}` | 删除指定会话 |
| GET | `/api/sessions/{session_id}` | 加载会话历史消息 |
| POST | `/api/chat` | 发送消息，AI 判题并回复 |

## ⚙️ 配置项

| 配置 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| API 密钥 | `DEEPSEEK_API_KEY_1` | 无 | DeepSeek API Key，必填 |
| 模型 | `DEEPSEEK_MODEL` | `deepseek-flash` | 可按需更换 |
| 数据库路径 | `DB_PATH` | `data/riddle.db` | SQLite 数据库文件位置 |
| Redis 地址 | `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | 缓存连接 |
| Redis 库 | `REDIS_DB` | `0` | 使用第几个库 |

## 架构说明（初学者向）

- **SQLite 会话表 `sessions`**：一个会话一行，聊天记录（`messages`）以 JSON 文本存进 `TEXT` 字段；表在应用启动时由 `db.init_db()` 自动创建。
- **Redis 缓存**：读会话、读 AI 回复都先查 Redis，命中即返回，未命中再查库/调模型并回填缓存；AI 回复缓存默认 24 小时过期。
- **降级策略**：Redis 连不上会自动跳过缓存继续运行；SQLite 内置无需服务，本地运行零配置。
