(function initAiAgentWidget() {
  const COPY = {
    title: "Chat mit uns",
    welcome:
      "Hallo! Beschreiben Sie kurz Ihr Anliegen — wir helfen bei Termin- oder Serviceanfragen.",
    placeholder: "Nachricht eingeben…",
    send: "Senden",
    sending: "Wird gesendet…",
    leadComplete:
      "Vielen Dank, wir haben alle nötigen Angaben. Wir melden uns in Kürze bei Ihnen.",
    genericError: "Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.",
    privacyWithLink:
      'Ihre Angaben werden zur Bearbeitung Ihrer Anfrage verwendet. <a href="{url}" target="_blank" rel="noopener noreferrer">Datenschutzerklärung</a>',
    privacyWithoutLink:
      "Ihre Angaben werden zur Bearbeitung Ihrer Anfrage verwendet.",
  };

  const RESTART_EVENT = "ai-agent-widget-restart";

  const script = document.currentScript;
  const container =
    document.querySelector("[data-ai-agent-widget]") ||
    document.getElementById("ai-agent-widget");

  if (!container) {
    console.error("AI Anfragen-Assistent widget: missing container element.");
    return;
  }

  const companySlug =
    container.dataset.companySlug ||
    script?.dataset.companySlug ||
    "demo-company";
  const installToken =
    container.dataset.installToken ||
    script?.dataset.installToken ||
    "";
  const apiBase = (
    container.dataset.apiBase ||
    script?.dataset.apiBase ||
    window.location.origin
  ).replace(/\/$/, "");
  const title = container.dataset.title || COPY.title;
  const privacyUrl = container.dataset.privacyUrl || "";
  const embedMode = container.dataset.embedMode === "panel";
  const welcomeMessage = container.dataset.welcomeMessage || COPY.welcome;

  let conversationId =
    container.dataset.conversationId ||
    `widget-${companySlug}-${Date.now()}`;

  const privacyHint = privacyUrl
    ? COPY.privacyWithLink.replace("{url}", privacyUrl)
    : COPY.privacyWithoutLink;

  function createConversationId() {
    return `widget-${companySlug}-${Date.now()}`;
  }

  function sendHeartbeat() {
    if (!installToken || !companySlug) {
      return;
    }

    const pageOrigin = window.location.origin;
    const storageKey = `ai-agent-heartbeat:${companySlug}:${pageOrigin}`;

    try {
      if (sessionStorage.getItem(storageKey)) {
        return;
      }
      sessionStorage.setItem(storageKey, "1");
    } catch {
      // sessionStorage may be unavailable; still attempt one heartbeat.
    }

    fetch(`${apiBase}/api/v1/public/widget/heartbeat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        company_slug: companySlug,
        install_token: installToken,
        page_origin: pageOrigin,
      }),
    }).catch(() => {
      // Heartbeat failure must not break chat.
    });
  }

  sendHeartbeat();

  const widgetClass = embedMode
    ? "ai-agent-widget ai-agent-widget--embedded"
    : "ai-agent-widget";

  container.innerHTML = `
    <div class="${widgetClass}">
      ${
        embedMode
          ? ""
          : `<div class="ai-agent-widget-header">${title}</div>`
      }
      <div class="ai-agent-widget-messages" role="log" aria-live="polite" aria-relevant="additions"></div>
      <p class="ai-agent-widget-privacy">${privacyHint}</p>
      <form class="ai-agent-widget-form">
        <div class="ai-agent-widget-composer">
          <input class="ai-agent-widget-input" type="text" placeholder="${COPY.placeholder}" autocomplete="off" />
          <button type="submit" class="ai-agent-widget-submit">${COPY.send}</button>
        </div>
      </form>
    </div>
  `;

  const messagesEl = container.querySelector(".ai-agent-widget-messages");
  const formEl = container.querySelector(".ai-agent-widget-form");
  const inputEl = container.querySelector(".ai-agent-widget-input");
  const submitEl = container.querySelector(".ai-agent-widget-submit");
  let loading = false;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function appendMessage(role, content) {
    const row = document.createElement("div");
    row.className = `ai-agent-widget-row ai-agent-widget-row--${role}`;

    const bubble = document.createElement("div");
    bubble.className = `ai-agent-widget-bubble ai-agent-widget-bubble--${role}`;
    bubble.innerHTML = escapeHtml(content).replace(/\n/g, "<br>");

    row.appendChild(bubble);
    messagesEl.appendChild(row);
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  function appendWelcome() {
    appendMessage("assistant", welcomeMessage);
  }

  function endChat() {
    loading = false;
    inputEl.disabled = true;
    submitEl.disabled = true;
    submitEl.textContent = COPY.send;
  }

  function setLoading(active) {
    loading = active;
    inputEl.disabled = active;
    submitEl.disabled = active;
    submitEl.textContent = active ? COPY.sending : COPY.send;
  }

  function restartConversation() {
    conversationId = createConversationId();
    container.dataset.conversationId = conversationId;
    messagesEl.innerHTML = "";
    appendWelcome();
    loading = false;
    inputEl.disabled = false;
    submitEl.disabled = false;
    submitEl.textContent = COPY.send;
    inputEl.focus();
  }

  async function sendMessage(message) {
    const response = await fetch(`${apiBase}/api/v1/public/widget/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        company_slug: companySlug,
        conversation_id: conversationId,
        message,
      }),
    });

    if (!response.ok) {
      let detail = COPY.genericError;
      try {
        const payload = await response.json();
        if (typeof payload.detail === "string") {
          detail = payload.detail;
        }
      } catch {
        // Keep generic error message.
      }
      throw new Error(detail);
    }

    return response.json();
  }

  formEl.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = inputEl.value.trim();
    if (!message || loading) {
      return;
    }

    setLoading(true);
    inputEl.value = "";
    appendMessage("user", message);

    let leadCompleted = false;
    try {
      const result = await sendMessage(message);
      appendMessage("assistant", result.reply);
      leadCompleted = Boolean(result.lead_complete);
      if (leadCompleted) {
        appendMessage("assistant", COPY.leadComplete);
      }
    } catch (error) {
      appendMessage(
        "assistant",
        error instanceof Error ? error.message : COPY.genericError,
      );
    } finally {
      if (leadCompleted) {
        endChat();
      } else {
        setLoading(false);
      }
    }
  });

  window.addEventListener(RESTART_EVENT, (event) => {
    const targetId = event.detail && event.detail.containerId;
    if (targetId && targetId !== container.id) {
      return;
    }
    restartConversation();
  });

  appendWelcome();
})();
