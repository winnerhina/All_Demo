# 💕 AI 智能伴侣

一个基于 **Streamlit + DeepSeek 大模型** 的 AI 伴侣聊天应用。你可以自由定制伴侣的**昵称**和**性格**，与 TA 进行微信聊天式的实时对话，支持流式输出、多会话管理，聊天的每一步都会自动保存。

本项目面向初学者，在基础聊天功能之上，额外加入了 **SQLite（本地数据库）**、**Redis（缓存）** 和 **Docker（容器化部署）**，方便你学习这三项常用技术。

## ✨ 功能特性

- 🤖 **定制专属伴侣**：自定义昵称和性格，塑造独一无二的 AI 伴侣
- 💬 **实时流式对话**：流式输出回复，像微信聊天一样自然
- 📂 **多会话管理**：支持新建、切换、删除会话，互不干扰
- 💾 **自动保存**：每次互动后自动保存会话到 **SQLite**，重启应用也不丢失
- ⚡ **Redis 缓存加速**：会话读缓存、AI 回复缓存，命中后不再重复调用大模型
- 🐳 **Docker 一键部署**：`docker compose up` 启动应用 + Redis

## 🛠️ 技术栈

- [Python 3.11+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) - Web 应用框架
- [OpenAI SDK](https://github.com/openai/openai-python) - 调用 DeepSeek API
- [DeepSeek API](https://platform.deepseek.com/) - 大模型接口
- [SQLite](https://www.sqlite.org/) - 本地单文件数据库（Python 内置，零配置）
- [Redis 7](https://redis.io/) - 会话/回复缓存
- [Docker](https://www.docker.com/) - 容器化部署

## 📁 目录结构

```
demo_AI_partner/
├── main.py               # 应用入口（页面、聊天逻辑、AI 回复缓存）
├── function.py           # 会话业务函数（保存/加载/删除，调用 db 和 cache）
├── db.py                 # SQLite 封装（建表 + 会话增删改查）
├── cache.py              # Redis 缓存封装（会话缓存 + AI 回复缓存）
├── config.py             # 集中配置（从环境变量/.env 读取连接信息）
├── requirements.txt      # Python 依赖
├── .env.example          # 环境变量示例（复制为 .env 后填写）
├── Dockerfile            # 应用镜像构建文件
├── docker-compose.yml    # 一键编排 app + Redis
├── data/                 # SQLite 数据库文件目录（运行时生成，已忽略）
└── resources/
    └── logo.png          # 应用 logo
```

## 🚀 快速开始

### 方式一：Docker 一键启动（推荐初学者）

需要先安装 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

```bash
cd demo_AI_partner

# 1. 准备密钥（复制示例文件并填入你的 DeepSeek Key）
cp .env.example .env     # Windows 用 copy .env.example .env

# 2. 构建并启动（应用 + Redis 两个容器）
docker compose up --build

# 3. 停止
docker compose down       # 加 -v 会连同数据卷一起删除
```

浏览器打开 `http://localhost:8501`。

### 方式二：本地运行

需要本机装好 Python；SQLite 内置无需安装，Redis 需要单独准备（本机安装，或用 `docker run -d -p 6379:6379 redis:7-alpine`）。

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（复制 .env.example 为 .env 并填写）
#    关键项：DEEPSEEK_API_KEY_1、DB_PATH、REDIS_HOST

# 3. 启动应用
streamlit run main.py
```

> Redis 如果连不上，程序会自动降级（跳过缓存继续运行）；SQLite 是数据存储，会自动在 `data/` 目录创建数据库文件。

## 🎯 使用说明

- **定制伴侣**：在左侧边栏输入想要的昵称和性格，例如「温柔体贴的学姐」「幽默搞笑的好兄弟」
- **新建会话**：点击侧边栏「新建会话」按钮，开始一段全新的对话
- **切换会话**：点击侧边栏的历史会话按钮，继续之前的聊天
- **删除会话**：点击会话旁的 ❌ 按钮删除对应会话

## ⚙️ 配置项

| 配置 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| API 密钥 | `DEEPSEEK_API_KEY_1` | 无 | DeepSeek API Key，必填 |
| 模型 | `DEEPSEEK_MODEL` | `deepseek-flash` | 可按需更换 |
| 数据库路径 | `DB_PATH` | `data/ai_partner.db` | SQLite 数据库文件位置 |
| Redis 地址 | `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | 缓存连接 |
| Redis 库 | `REDIS_DB` | `0` | 使用第几个库 |

## 📝 架构说明（初学者向）

- **SQLite 会话表 `sessions`**：一个会话一行，聊天记录（`messages`）以 JSON 文本存进 `TEXT` 字段；表在应用启动时由 `db.init_db()` 自动创建。
- **Redis 缓存**：读会话、读 AI 回复都先查 Redis，命中即返回，未命中再查库/调模型并回填缓存；AI 回复缓存默认 24 小时过期。
- **降级策略**：Redis 连不上会自动跳过缓存继续运行；SQLite 内置无需服务，本地运行零配置。

## 📄 许可证

本项目仅供个人学习使用。