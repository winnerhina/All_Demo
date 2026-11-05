/* =====================================================
 * 汉字谜盒 —— 前端交互逻辑（RESTful 版）
 * 说明：本文件仅负责界面交互与发起 RESTful 请求。
 * 会话的新建 / 列表 / 删除，以及消息发送均由后端接口处理，
 * 前端不直接创建会话数据，严格遵循 RESTful 规范。
 *
 * 后端需实现的 REST 接口（资源用复数、动词由 HTTP 方法表达）：
 *   POST   /sessions            新建会话
 *   GET    /sessions            获取会话列表
 *   DELETE /sessions/{id}       删除某个会话
 *   GET    /sessions/{id}       获取某个会话的聊天历史
 *   POST   /api/chat            向聊天发送消息
 * ===================================================== */

(function () {
  "use strict";

  // ---- RESTful API 基础地址 ----
  const API = "/api/sessions";

  // ---- DOM 引用 ----
  const historyList = document.getElementById("history-list");
  const chatMessages = document.getElementById("chat-messages");
  const chatEmpty = document.getElementById("chat-empty");
  const sessionName = document.getElementById("session-name");
  const messageInput = document.getElementById("message-input");
  const btnSend = document.getElementById("btn-send");
  const btnNewGame = document.getElementById("btn-new-game");

  // ---- 当前会话状态（仅保存"正在查看哪个会话"，数据本体在后端） ----
  let sessions = [];        // 会话ID字符串数组（后端返回，最新在前）
  let currentSessionId = null;

  /**
   * 在网页上显示一条错误提示（红色横幅，自动消失）
   * @param {string} message 提示内容
   */
  function showError(message) {
    const banner = document.createElement("div");
    banner.className = "error-banner";
    banner.textContent = "⚠ " + message;
    banner.style.cssText =
      "position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:9999;" +
      "background:#e5484d;color:#fff;padding:10px 18px;border-radius:8px;" +
      "font-size:14px;box-shadow:0 4px 14px rgba(0,0,0,.35);max-width:90%;";
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 4000);
  }

  /**
   * 统一的请求封装：将 HTTP 动词 + URL + 请求体转换为 fetch 调用，
   * 以此表达 CRUD 语义（这就是 RESTful 的核心：用方法表达操作）。
   * 后端所有接口统一返回 {code, message, date} 包装格式，
   * 此处自动解包，调用方拿到的就是 date 里的真正数据。
   * @param {string} method  HTTP 动词（GET / POST / PUT / DELETE）
   * @param {string} url     资源路径（以 / 开头）
   * @param {object} [body]  可选的请求体（对象）
   */
  async function request(method, url, body) {
    const opts = { method, headers: { "Content-Type": "application/json" } };
    if (body !== undefined) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    // 204 无内容返回 null
    if (res.status === 204) return null;
    const data = await res.json();
    // 统一解包：响应是 {code, message, date} 时，只返回 date 部分
    if (data && typeof data === "object" && "date" in data) {
      return data.date;
    }
    // 兼容图片中的 {code, message, data} 包装格式
    if (data && typeof data === "object" && "data" in data) {
      return data.data;
    }
    return data;   // 兼容非包装格式
  }

  // ---- 会话 API 封装（严格对应 RESTful 资源操作） ----
  const sessionsApi = {
    async create()   { return request("POST", API); },                 // 新建
    async list()     { return request("GET", API); },                  // 查询列表
    async remove(id) { return request("DELETE", `${API}/${id}`); },    // 删除单个
  };

  const messagesApi = {
    async send(id, message) { return request("POST", "/api/chat", { session_id: id, message }); },
    async list(id)          { return request("GET", `/api/sessions/${id}`); },
  };

  /**
   * 根据聊天区是否有消息，控制空态图案（魔法棒+提示文字）的显示/隐藏。
   */
  function updateChatEmpty() {
    const hasMsg = chatMessages.querySelector(".message-group") !== null;
    if (chatEmpty) chatEmpty.style.display = hasMsg ? "none" : "flex";
  }

  /**
   * 创建新消息气泡
   * @param {string} text 消息内容
   * @param {string} who  'ai' 或 'user'
   */
  function appendMessage(text, who) {
    const group = document.createElement("div");
    group.className = "message-group " + who;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = who === "ai" ? "🤖" : "👤";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    if (who === "ai") {
      group.append(avatar, bubble);
    } else {
      group.append(bubble, avatar);
    }

    chatMessages.appendChild(group);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    updateChatEmpty();
  }

  /**
   * 渲染某个会话的全部历史消息到聊天区
   * @param {Array} msgs 后端返回的消息数组 [{role, content}, ...]
   */
  function renderMessages(msgs) {
    chatMessages.innerHTML = "";
    (msgs || []).forEach((m) => {
      const who = m.role === "user" ? "user" : "ai";
      appendMessage(m.content, who);
    });
    updateChatEmpty();
  }

  // ---- 历史记录渲染（sessions 为后端返回的会话ID字符串数组，最新在前） ----
  function renderHistory() {
    historyList.innerHTML = "";
    sessions.forEach((sid) => {
      const li = document.createElement("li");
      li.className = "history-item" + (sid === currentSessionId ? " active" : "");
      li.dataset.id = sid;

      const span = document.createElement("span");
      span.className = "timestamp";
      span.textContent = sid;

      const btnDel = document.createElement("button");
      btnDel.className = "btn-delete";
      btnDel.textContent = "✕";
      btnDel.title = "删除会话";
      btnDel.addEventListener("click", (e) => {
        e.stopPropagation();
        deleteSession(sid);
      });

      li.appendChild(span);
      li.appendChild(btnDel);

      li.addEventListener("click", () => selectSession(sid));

      historyList.appendChild(li);
    });
  }

  /**
   * 加载历史会话列表：只保留请求接口
   * GET /api/sessions → data 为会话ID字符串数组（最新在前），
   * 列表数据与排序均由后端负责，前端仅渲染，当前会话取第一条。
   */
  async function loadSessions() {
    try {
      sessions = await sessionsApi.list();
      currentSessionId = sessions.length ? sessions[0] : null;
      sessionName.textContent = currentSessionId
        ? "会话名称：" + currentSessionId
        : "会话名称：--";
      renderHistory();
    } catch (err) {
      console.error("加载会话列表失败：", err);
      showError("加载会话列表失败，请确认后端接口运行正常。");
    }
  }

  // ---- 新建游戏（只保留请求接口：走后端 POST /sessions，创建后重新拉取列表） ----
  async function newGame() {
    try {
      await sessionsApi.create();
      await loadSessions();
      chatMessages.innerHTML = "";
      updateChatEmpty();
      messageInput.focus();
    } catch (err) {
      console.error("新建会话失败：", err);
      showError("新建会话失败，请确认后端接口运行正常。");
    }
  }

  // ---- 切换会话（点击聊天记录 → 向后端请求该会话的历史消息） ----
  async function selectSession(id) {
    currentSessionId = id;
    renderHistory();
    sessionName.textContent = "会话名称：" + id;

    // GET /api/sessions/{id} → data 为 {current_session, messages: [{role, content}]}
    try {
      const data = await messagesApi.list(id);
      renderMessages(data.messages || data);
    } catch (err) {
      console.error("加载会话历史失败：", err);
      showError("加载会话历史失败，请确认后端接口运行正常。");
      chatMessages.innerHTML = "";
      updateChatEmpty();
    }
  }

  // ---- 删除会话（走后端 DELETE /sessions/{id}，删除后重新拉取列表） ----
  async function deleteSession(id) {
    const wasCurrent = id === currentSessionId;
    try {
      await sessionsApi.remove(id);                  // 由后端删除
      await loadSessions();                          // 重新拉取列表，自动选中第一条
      if (wasCurrent) {
        // 删的是当前会话：清空聊天区，并加载新当前会话的历史消息
        chatMessages.innerHTML = "";
        updateChatEmpty();
        if (currentSessionId) await selectSession(currentSessionId);
      }
    } catch (err) {
      console.error("删除会话失败：", err);
      showError("删除会话失败，请确认后端接口运行正常。");
    }
  }

  /**
   * 在聊天区追加一个"AI 正在输入"的占位气泡（三个点加载动画）。
   * @returns {HTMLElement} 该气泡所在的 .message-group，等待结束后移除
   */
  function appendTyping() {
    const group = document.createElement("div");
    group.className = "message-group ai typing-group";

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "🤖";

    const bubble = document.createElement("div");
    bubble.className = "bubble typing-bubble";
    // 三个点，用 CSS 动画做成依次闪烁
    bubble.innerHTML =
      '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';

    group.append(avatar, bubble);
    chatMessages.appendChild(group);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return group;
  }

  /** 移除"正在输入"占位气泡 */
  function removeTyping(group) {
    if (group && group.parentNode) group.parentNode.removeChild(group);
    updateChatEmpty();
  }

  // ---- 发送消息（走后端 POST /api/chat） ----
  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || !currentSessionId) return;

    appendMessage(text, "user");
    messageInput.value = "";

    // 等待 AI 回答期间，显示"正在输入"的加载气泡
    const typingGroup = appendTyping();

    try {
      // request() 已解包，date/data 可能是字符串（图片格式）或对象 {reply}
      const reply = await messagesApi.send(currentSessionId, text);
      const replyText =
        typeof reply === "string"
          ? reply
          : (reply && (reply.reply || reply.message)) || "（后端已收到消息，当前无回复内容）";
      removeTyping(typingGroup);
      appendMessage(replyText, "ai");
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (err) {
      console.error("发送消息失败：", err);
      removeTyping(typingGroup);
      appendMessage("（消息发送失败，请确认后端接口运行正常）", "ai");
    }
  }

  // ---- 事件绑定 ----
  btnSend.addEventListener("click", sendMessage);
  btnNewGame.addEventListener("click", newGame);
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // ---- 页面初始化：自动加载会话列表，并新建一个会话 ----
  window.addEventListener("DOMContentLoaded", async () => {
    await loadSessions();   // 1. 自动加载历史会话列表
    await newGame();        // 2. 自动新建一个会话
    // 任一步失败时，对应的 catch 内已调用 showError 在网页上提示
  });
})();