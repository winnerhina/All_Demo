# AI 伙伴

一个基于 Python、Streamlit 和 DeepSeek API 的角色聊天应用。可以设置 AI 的昵称和性格，查看逐步显示的回复，并将聊天记录保存到本地 JSON 文件。

## 功能

- 自定义 AI 昵称和性格。
- 逐步显示模型回复，即流式输出。
- 新建、切换和删除会话。
- 自动保存角色设置和聊天记录，重启后可恢复并继续聊天。

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
python -m streamlit run main.py
```

浏览器打开 `http://localhost:8501`。

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
| `main.py` | Streamlit 页面入口，显示角色设置与聊天界面，调用模型并逐步显示回复 |
| `function.py` | 生成会话编号，在本地 JSON 文件中保存、读取、列出与删除会话 |
| `config.py` | 读取模型配置和聊天记录目录 |
| `.env.example` | 不含真实密钥的配置示例 |
| `requirements.txt` | 运行项目所需的 Python 库 |
| `.gitignore` | 避免提交聊天记录、密钥、日志和临时文件 |
| `resources/logo.png` | 页面图标与应用标识 |
| `tests/test_json_storage.py` | 检查记录保存恢复、旧格式兼容、写入失败保护及页面聊天、切换、删除流程 |
| `README.md` | 项目说明、运行步骤和文件用途 |
