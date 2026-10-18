# 💕 AI 智能伴侣

一个基于 **Streamlit + DeepSeek 大模型** 的 AI 伴侣聊天应用。你可以自由定制伴侣的**昵称**和**性格**，与 TA 进行微信聊天式的实时对话，支持流式输出、多会话管理，聊天的每一步都会自动保存。

## ✨ 功能特性

- 🤖 **定制专属伴侣**：自定义昵称和性格，塑造独一无二的 AI 伴侣
- 💬 **实时流式对话**：流式输出回复，像微信聊天一样自然
- 📂 **多会话管理**：支持新建、切换、删除会话，互不干扰
- 💾 **自动保存**：每次互动后自动保存会话，重启应用也不丢失聊天记录
- 🔄 **历史会话加载**：侧边栏一键切换到任意历史会话，继续之前的话题

## 🛠️ 技术栈

- [Python 3.11+](https://www.python.org/)
- [Streamlit](https://streamlit.io/) - Web 应用框架
- [OpenAI SDK](https://github.com/openai/openai-python) - 调用 DeepSeek API
- [DeepSeek API](https://platform.deepseek.com/) - 大模型接口

## 📁 目录结构

```
Project_AI_partner/
├── AI_Partner/
│   ├── main.py               # 应用入口（页面、聊天逻辑）
│   ├── function.py           # 会话保存/加载/删除辅助函数
│   ├── resources/
│   │   └── logo.png          # 应用 logo
│   └── sessions/             # 会话记录（运行时生成，已被 .gitignore 忽略）
└── .gitignore
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install streamlit openai
```

### 2. 配置 API 密钥

本应用通过环境变量读取 DeepSeek API 密钥（密钥不会写入代码或仓库）：

**Windows (PowerShell)：**

```powershell
# 临时生效（当前窗口）
$env:DEEPSEEK_API_KEY_1 = "你的DeepSeek密钥"

# 永久生效
setx DEEPSEEK_API_KEY_1 "你的DeepSeek密钥"
```

**macOS / Linux：**

```bash
export DEEPSEEK_API_KEY_1="你的DeepSeek密钥"
```

> 没有密钥？前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 注册并创建 API Key。

### 3. 启动应用

```bash
cd AI_Partner
streamlit run main.py
```

浏览器自动打开 `http://localhost:8501`，开始和你的 AI 伴侣聊天吧！

## 🎯 使用说明

- **定制伴侣**：在左侧边栏输入想要的昵称和性格，例如「温柔体贴的学姐」「幽默搞笑的好兄弟」
- **新建会话**：点击侧边栏「新建会话」按钮，开始一段全新的对话
- **切换会话**：点击侧边栏的历史会话按钮，继续之前的聊天
- **删除会话**：点击会话旁的 ❌ 按钮删除对应会话

## ⚙️ 配置项

| 配置 | 环境变量 | 说明 |
|------|----------|------|
| API 密钥 | `DEEPSEEK_API_KEY_1` | DeepSeek API Key，必填 |
| 模型 | `main.py` 中 `model="deepseek-flash"` | 可按需更换为 `deepseek-chat` / `deepseek-reasoner` |

## 📝 说明

- 会话记录以 JSON 格式保存在 `sessions/` 目录
- 本项目仅用于学习和娱乐，请遵守 DeepSeek 平台的使用规范

## 📄 许可证

本项目仅供个人学习使用。
