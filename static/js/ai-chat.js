document.addEventListener("DOMContentLoaded", () => {
    const trigger = document.getElementById("ai-chat-trigger");
    const window_ = document.getElementById("ai-chat-window");
    if (!trigger || !window_) return;

    const messagesEl = window_.querySelector(".ai-chat-messages");
    const input = window_.querySelector(".ai-chat-input");
    const sendBtn = window_.querySelector(".ai-chat-send");
    const newChatBtn = window_.querySelector(".ai-chat-new");
    const toggleSessionsBtn = window_.querySelector(".ai-chat-toggle-sessions");
    const sessionsPanel = window_.querySelector(".ai-chat-sessions");
    const sessionList = window_.querySelector(".ai-chat-session-list");

    let currentSessionId = null;
    let isStreaming = false;

    // Load marked.js for Markdown rendering
    const markedScript = document.createElement("script");
    markedScript.src = "https://cdn.jsdelivr.net/npm/marked@14/marked.min.js";
    document.head.appendChild(markedScript);

    // Toggle chat window
    trigger.addEventListener("click", () => {
        const isOpen = window_.classList.toggle("open");
        trigger.classList.toggle("hidden", isOpen);
        if (isOpen && sessionList.children.length === 0) {
            loadSessions();
        }
        if (isOpen) {
            setTimeout(() => input.focus(), 200);
        }
    });

    // Close button
    window_.querySelector(".ai-chat-close").addEventListener("click", () => {
        window_.classList.remove("open");
        trigger.classList.remove("hidden");
    });

    // New chat
    newChatBtn.addEventListener("click", () => {
        currentSessionId = null;
        messagesEl.innerHTML = renderWelcome();
        input.focus();
    });

    // Toggle sessions panel
    toggleSessionsBtn.addEventListener("click", () => {
        sessionsPanel.classList.toggle("show");
        if (sessionsPanel.classList.contains("show")) {
            loadSessions();
        }
    });

    // Send message
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    input.addEventListener("input", () => {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 120) + "px";
    });

    function sendMessage() {
        const content = input.value.trim();
        if (!content || isStreaming) return;

        // Clear welcome message if present
        const welcome = messagesEl.querySelector(".ai-welcome");
        if (welcome) welcome.remove();

        // Add user message
        appendMessage("user", content);
        input.value = "";
        input.style.height = "auto";

        // Add assistant placeholder
        const assistantEl = appendMessage("assistant", "", true);
        isStreaming = true;
        sendBtn.disabled = true;

        // Send to backend
        fetch("/ai/api/stream/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSessionId,
                content: content,
            }),
        }).then((response) => {
            if (!response.ok) {
                return response.json().then((data) => {
                    throw new Error(data.error || "请求失败");
                });
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";
            let fullContent = "";

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        finishStream(assistantEl, fullContent);
                        return;
                    }

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split("\n");
                    buffer = lines.pop();

                    for (const line of lines) {
                        if (!line.startsWith("data: ")) continue;
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.error) {
                                assistantEl.classList.add("error");
                                assistantEl.classList.remove("assistant");
                                assistantEl.textContent = data.error;
                                finishStream(assistantEl, data.error);
                                return;
                            }
                            if (data.token) {
                                fullContent += data.token;
                                renderMarkdown(assistantEl, fullContent);
                                scrollToBottom();
                            }
                            if (data.done) {
                                if (data.session_id && !currentSessionId) {
                                    currentSessionId = data.session_id;
                                }
                                finishStream(assistantEl, fullContent);
                                return;
                            }
                        } catch (e) {
                            // skip parse errors
                        }
                    }
                    read();
                });
            }
            read();
        }).catch((err) => {
            assistantEl.classList.add("error");
            assistantEl.classList.remove("assistant");
            assistantEl.textContent = err.message || "网络错误";
            finishStream(assistantEl, err.message);
        });
    }

    function finishStream(el, content) {
        el.classList.remove("ai-typing");
        if (content && !el.classList.contains("error")) {
            renderMarkdown(el, content);
        }
        isStreaming = false;
        sendBtn.disabled = false;
        input.focus();
    }

    function appendMessage(role, content, isTyping = false) {
        const div = document.createElement("div");
        div.className = `ai-msg ${role}`;
        if (isTyping) div.classList.add("ai-typing");
        if (content) {
            if (role === "assistant") {
                renderMarkdown(div, content);
            } else {
                div.textContent = content;
            }
        }
        messagesEl.appendChild(div);
        scrollToBottom();
        return div;
    }

    function renderMarkdown(el, text) {
        if (typeof marked !== "undefined" && marked.parse) {
            el.innerHTML = marked.parse(text);
        } else {
            el.textContent = text;
        }
    }

    function renderWelcome() {
        return `<div class="ai-welcome">
            <strong>AI 资产助手</strong>
            你好！我是企业资产管理系统的 AI 助手。<br>
            你可以问我关于资产、领用、维修等方面的问题。
        </div>`;
    }

    function scrollToBottom() {
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function loadSessions() {
        fetch("/ai/api/sessions/")
            .then((r) => r.json())
            .then((sessions) => {
                sessionList.innerHTML = "";
                if (sessions.length === 0) {
                    sessionList.innerHTML = '<div style="padding:8px;color:var(--muted);font-size:0.85rem;">暂无历史会话</div>';
                    return;
                }
                sessions.forEach((s) => {
                    const div = document.createElement("div");
                    div.className = "ai-chat-session-item" + (s.id === currentSessionId ? " active" : "");
                    div.dataset.id = s.id;
                    div.textContent = s.title;
                    div.addEventListener("click", () => loadSession(s.id));
                    sessionList.appendChild(div);
                });
            });
    }

    function loadSession(id) {
        currentSessionId = id;
        messagesEl.innerHTML = "";
        sessionsPanel.classList.remove("show");

        fetch(`/ai/api/sessions/${id}/`)
            .then((r) => r.json())
            .then((data) => {
                if (data.messages) {
                    data.messages.forEach((msg) => {
                        appendMessage(msg.role, msg.content);
                    });
                }
                // Update active state in session list
                sessionList.querySelectorAll(".ai-chat-session-item").forEach((el) => {
                    el.classList.toggle("active", el.dataset.id === String(id));
                });
            });
    }
});
