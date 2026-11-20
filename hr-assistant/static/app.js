const messagesEl = document.getElementById("messages");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const WELCOME = messagesEl.innerHTML;

const convListEl = document.getElementById("conv-list");
const sidebarEl = document.getElementById("sidebar");

let conversationId = null;
// incremented every time the user switches conversation, so a slow reply that arrives
// after switching is not drawn into the wrong conversation
let view = 0;

function addMessage(text, cls) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.textContent = text; // textContent keeps model output as plain text
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

async function send(text) {
  const myView = view;
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
    // the first message of a new chat creates the conversation: show it in the sidebar
    loadConversations();
    if (myView !== view) return; // user switched conversation meanwhile; reply is saved server-side
    conversationId = data.conversation_id;
    markActive();
    addMessage(data.response, "bot");
  } catch (err) {
    typing.remove();
    if (myView === view) addMessage("Error: " + err.message, "bot error");
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

// ---- conversations sidebar ----

function cleanTitle(t) {
  return (t || "Untitled").replace(/^New Conversation:\s*/, "");
}

function markActive() {
  for (const li of convListEl.children) {
    li.classList.toggle("active", Number(li.dataset.id) === conversationId);
  }
}

async function loadConversations() {
  try {
    const res = await fetch("/conversations");
    const convs = await res.json();
    convListEl.innerHTML = "";
    for (const c of convs) {
      const li = document.createElement("li");
      li.dataset.id = c.id;
      li.textContent = cleanTitle(c.title); // textContent: titles come from user text
      li.title = li.textContent;
      li.addEventListener("click", () => openConversation(c.id));
      convListEl.appendChild(li);
    }
    markActive();
  } catch (err) {
    console.error("Could not load conversations", err);
  }
}

async function openConversation(id) {
  view++;
  conversationId = id;
  markActive();
  sidebarEl.classList.remove("open"); // close the drawer on mobile
  messagesEl.innerHTML = "";
  const myView = view;
  try {
    const res = await fetch("/conversations/" + id + "/messages");
    if (!res.ok) throw new Error("Request failed (" + res.status + ")");
    const msgs = await res.json();
    if (myView !== view) return; // user clicked something else while loading
    for (const m of msgs) addMessage(m.content, m.role === "user" ? "user" : "bot");
  } catch (err) {
    if (myView === view) addMessage("Error: " + err.message, "bot error");
  }
  input.focus();
}

function newChat() {
  view++;
  conversationId = null;
  messagesEl.innerHTML = WELCOME;
  markActive();
  sidebarEl.classList.remove("open");
  input.focus();
}

document.getElementById("new-chat").addEventListener("click", newChat);
document.getElementById("toggle-side").addEventListener("click", () => sidebarEl.classList.toggle("open"));

loadConversations();
