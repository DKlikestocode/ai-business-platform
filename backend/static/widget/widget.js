(function initAiAgentWidget() {
  const COPY = {
    title: "Chat mit uns",
    placeholder: "Nachricht eingeben…",
    send: "Senden",
    sending: "Wird gesendet…",
    userLabel: "Sie",
    assistantLabel: "Assistent",
    leadComplete:
      "Vielen Dank, wir haben alle nötigen Angaben. Wir melden uns in Kürze bei Ihnen.",
    genericError: "Etwas ist schiefgelaufen. Bitte versuchen Sie es erneut.",
    privacyWithLink:
      'Ihre Angaben werden zur Bearbeitung Ihrer Anfrage verwendet. <a href="{url}" target="_blank" rel="noopener noreferrer" style="color:#2563eb;">Datenschutzerklärung</a>',
    privacyWithoutLink:
      "Ihre Angaben werden zur Bearbeitung Ihrer Anfrage verwendet.",
  };

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
  const conversationId =
    container.dataset.conversationId ||
    `widget-${companySlug}-${Date.now()}`;

  const privacyHint = privacyUrl
    ? COPY.privacyWithLink.replace("{url}", privacyUrl)
    : COPY.privacyWithoutLink;

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

  container.innerHTML = `
    <div class="ai-agent-widget" style="font-family:Inter,system-ui,sans-serif;border:none;border-radius:0;overflow:hidden;max-width:none;width:100%;background:#fff;">
      <div style="padding:14px 16px;background:linear-gradient(135deg,#2563eb 0%,#1d4ed8 100%);color:#fff;font-weight:600;font-size:0.95rem;">${title}</div>
      <div class="ai-agent-widget-messages" style="height:300px;overflow:auto;padding:16px;background:#f8fafc;"></div>
      <p class="ai-agent-widget-privacy" style="margin:0;padding:10px 14px 0;font-size:11px;line-height:1.45;color:#64748b;">${privacyHint}</p>
      <form class="ai-agent-widget-form" style="display:flex;gap:8px;padding:14px;border-top:1px solid #e2e8f0;background:#fff;">
        <input class="ai-agent-widget-input" type="text" placeholder="${COPY.placeholder}" style="flex:1;padding:11px 12px;border:1px solid #cbd5e1;border-radius:10px;font-size:0.92rem;" />
        <button type="submit" class="ai-agent-widget-submit" style="padding:11px 16px;border:none;border-radius:10px;background:#2563eb;color:#fff;font-weight:600;font-size:0.92rem;">${COPY.send}</button>
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
    const bubble = document.createElement("div");
    bubble.style.marginBottom = "10px";
    bubble.innerHTML = `<strong style="display:block;font-size:12px;color:#6b7280;margin-bottom:4px;">${
      role === "user" ? COPY.userLabel : COPY.assistantLabel
    }</strong><div>${escapeHtml(content)}</div>`;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
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
})();
