const messagesEl = document.getElementById("messages");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const WELCOME = messagesEl.innerHTML;

let conversationId = null;

function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.textContent = text; // textContent keeps model output as plain text
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function send(text) {
  addMessage(text, "user");
  const typing = addMessage("", "bot typing");
  typing.innerHTML = "<span></span><span></span><span></span>";
  sendBtn.disabled = true;

  let url = "/chat?message=" + encodeURIComponent(text);
  if (conversationId !== null) url += "&conversation_id=" + conversationId;

  try {
    const res = await fetch(url);
    const data = await res.json();
    typing.remove();
    if (!res.ok) throw new Error(data.detail || "Request failed (" + res.status + ")");
    conversationId = data.conversation_id;
    addMessage(data.response, "bot");
  } catch (err) {
    typing.remove();
    addMessage("Error: " + err.message, "bot error");
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text || sendBtn.disabled) return;
  input.value = "";
  input.style.height = "auto";
  send(text);
});

// Enter sends, Shift+Enter adds a newline
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = input.scrollHeight + "px";
});

document.getElementById("new-chat").addEventListener("click", () => {
  conversationId = null;
  messagesEl.innerHTML = WELCOME;
  input.focus();
});
