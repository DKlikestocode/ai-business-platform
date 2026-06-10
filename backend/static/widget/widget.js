(function initAiAgentWidget() {
  const script = document.currentScript;
  const container =
    document.querySelector("[data-ai-agent-widget]") ||
    document.getElementById("ai-agent-widget");

  if (!container) {
    console.error("AI Agent widget: missing container element.");
    return;
  }

  const companySlug =
    container.dataset.companySlug ||
    script?.dataset.companySlug ||
    "demo-company";
  const apiBase = (
    container.dataset.apiBase ||
    script?.dataset.apiBase ||
    window.location.origin
  ).replace(/\/$/, "");
  const title = container.dataset.title || "Chat with us";
  const conversationId =
    container.dataset.conversationId ||
    `widget-${companySlug}-${Date.now()}`;

  container.innerHTML = `
    <div class="ai-agent-widget" style="font-family:Inter,system-ui,sans-serif;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;max-width:420px;background:#fff;">
      <div style="padding:12px 16px;background:#2563eb;color:#fff;font-weight:600;">${title}</div>
      <div class="ai-agent-widget-messages" style="height:280px;overflow:auto;padding:16px;background:#f9fafb;"></div>
      <form class="ai-agent-widget-form" style="display:flex;gap:8px;padding:12px;border-top:1px solid #e5e7eb;">
        <input class="ai-agent-widget-input" type="text" placeholder="Type your message..." style="flex:1;padding:10px 12px;border:1px solid #d1d5db;border-radius:8px;" />
        <button type="submit" style="padding:10px 14px;border:none;border-radius:8px;background:#2563eb;color:#fff;font-weight:600;">Send</button>
      </form>
    </div>
  `;

  const messagesEl = container.querySelector(".ai-agent-widget-messages");
  const formEl = container.querySelector(".ai-agent-widget-form");
  const inputEl = container.querySelector(".ai-agent-widget-input");
  let loading = false;

  function appendMessage(role, content) {
    const bubble = document.createElement("div");
    bubble.style.marginBottom = "10px";
    bubble.innerHTML = `<strong style="display:block;font-size:12px;color:#6b7280;margin-bottom:4px;">${
      role === "user" ? "You" : "Assistant"
    }</strong><div>${content}</div>`;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
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
      let detail = `Request failed (${response.status})`;
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

    loading = true;
    inputEl.value = "";
    appendMessage("user", message);

    try {
      const result = await sendMessage(message);
      appendMessage("assistant", result.reply);
      if (result.lead_complete) {
        appendMessage(
          "assistant",
          "Thanks, we have everything we need. Someone will follow up soon.",
        );
        inputEl.disabled = true;
        formEl.querySelector("button").disabled = true;
      }
    } catch (error) {
      appendMessage(
        "assistant",
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      loading = false;
    }
  });
})();
