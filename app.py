import streamlit as st
from dotenv import load_dotenv
import os
import time
import random
import uuid
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# LangChain Models
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

# ---------------------------------------------------
# LOAD ENV VARIABLES
# ---------------------------------------------------
load_dotenv()

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Multi-Model Chatbot",
    page_icon="🤖",
    layout="centered"
)

# ---------------------------------------------------
# SYSTEM PROMPT
# ---------------------------------------------------
SYSTEM_PROMPT = """
You are a helpful Multi-Models AI Assistant Chatbot. You answer questions clearly,
 accurately, and concisely. You adapt your tone to the user: professional when 
 needed, friendly when appropriate. You are also a senior developoer: You can 
 do coding in any programming language You are AI Engineer expert: You can 
 design and deploy intelligent systems. You are a Data scientist and analyst
 expert: You can collect, analyze, and interpret complex data to gain insights
 and inform business decisions. You are a Business Intelligence Analyst expert:
 You can analyze business data to identify trends, opportunities, and areas for improvement. 
 You are also a Supply Chain Analyst expert: You can optimize and streamline logistics,
 procurement, and distribution processes to improve efficiency and reduce costs. 
 You explain complex ideas in simple terms and provide practical examples when helpful.
 You avoid unnecessary repetition, hallucinations, and overly verbose responses. 
 Your goal is to genuinely help the user solve problems, learn, or make decisions.
 Always refer to me as "My friend" when you answer any question or request
"""

# ---------------------------------------------------
# AVATARS
# ---------------------------------------------------
USER_AVATAR    = "🧑‍💻"
ASSISTANT_AVATAR = "🤖"

# ---------------------------------------------------
# PROVIDERS & MODELS
# ---------------------------------------------------
MODELS = {
    "Groq":   ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    "OpenAI": ["gpt-3.5-turbo", "gpt-4.1"],
    "Gemini": ["gemini-2.5-pro", "gemini-2.5-flash"],
    "Ollama": ["gemma3", "llama3.1"],
}

# ---------------------------------------------------
# PERSISTENCE — always saved in the working directory
# (the folder you ran `streamlit run app.py` from)
# ---------------------------------------------------
HISTORY_FILE = Path(os.getcwd()) / "chat_history.json"

def save_chats():
    """Write all chats to disk as JSON."""
    data = {
        "current_chat_id": st.session_state.current_chat_id,
        "chats": st.session_state.chats,
    }
    HISTORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def load_chats():
    """
    Load chats from disk.
    Returns (chats, current_chat_id) or (None, None) if file missing / corrupt.
    """
    if not HISTORY_FILE.exists():
        return None, None
    try:
        data = json.loads(HISTORY_FILE.read_text())
        chats = data.get("chats", [])
        cid   = data.get("current_chat_id")
        # Validate: make sure referenced id actually exists
        ids = {c["id"] for c in chats}
        if cid not in ids and chats:
            cid = chats[0]["id"]
        return chats, cid
    except Exception:
        return None, None

# ---------------------------------------------------
# LOAD MODEL (cached)
# ---------------------------------------------------
@st.cache_resource
def load_model(provider, model_name):
    if provider == "OpenAI":
        return ChatOpenAI(
            model=model_name, temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif provider == "Gemini":
        return ChatGoogleGenerativeAI(
            model=model_name, temperature=0.7,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    elif provider == "Groq":
        return ChatGroq(
            model=model_name, temperature=0.7,
            api_key=os.getenv("GROQ_API_KEY"),
            model_kwargs={"top_p": 0.9}
        )
    elif provider == "Ollama":
        return ChatOllama(model=model_name, temperature=0.7)

# ---------------------------------------------------
# TYPEWRITER EFFECT
# ---------------------------------------------------
def typewriter(text, delay=0.01):
    for char in text:
        yield char
        time.sleep(delay)

# ---------------------------------------------------
# CHAT HELPERS
# ---------------------------------------------------
def make_chat(provider, model):
    return {
        "id":         str(uuid.uuid4()),
        "title":      "New Chat",
        "messages":   [],
        "provider":   provider,
        "model":      model,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

def current_chat():
    cid = st.session_state.current_chat_id
    for chat in st.session_state.chats:
        if chat["id"] == cid:
            return chat
    return st.session_state.chats[0]

def switch_to(chat_id):
    st.session_state.current_chat_id = chat_id
    save_chats()

def delete_chat(chat_id):
    st.session_state.chats = [c for c in st.session_state.chats if c["id"] != chat_id]
    if st.session_state.current_chat_id == chat_id:
        if st.session_state.chats:
            st.session_state.current_chat_id = st.session_state.chats[0]["id"]
        else:
            new = make_chat(
                st.session_state.get("active_provider", list(MODELS)[0]),
                st.session_state.get("active_model",   MODELS[list(MODELS)[0]][0]),
            )
            st.session_state.chats            = [new]
            st.session_state.current_chat_id  = new["id"]
    save_chats()

def group_chats_by_date(chats):
    """Return dict: {'Today': [...], 'Yesterday': [...], 'Last 7 days': [...], 'Older': [...]}"""
    today     = date.today()
    yesterday = today - timedelta(days=1)
    week_ago  = today - timedelta(days=7)

    groups = {"Today": [], "Yesterday": [], "Last 7 days": [], "Older": []}
    for chat in chats:
        try:
            d = datetime.fromisoformat(chat.get("updated_at", chat.get("created_at", ""))).date()
        except Exception:
            d = date.min
        if d == today:
            groups["Today"].append(chat)
        elif d == yesterday:
            groups["Yesterday"].append(chat)
        elif d > week_ago:
            groups["Last 7 days"].append(chat)
        else:
            groups["Older"].append(chat)
    return groups

# ---------------------------------------------------
# SESSION STATE INITIALISATION
# ---------------------------------------------------
if "chats" not in st.session_state:
    persisted_chats, persisted_cid = load_chats()
    if persisted_chats:
        st.session_state.chats           = persisted_chats
        st.session_state.current_chat_id = persisted_cid
    else:
        initial = make_chat(list(MODELS)[0], MODELS[list(MODELS)[0]][0])
        st.session_state.chats           = [initial]
        st.session_state.current_chat_id = initial["id"]
        # FIX 2: write the file immediately so the first refresh can read it
        save_chats()

# FIX 3: seed active_provider / active_model from the restored chat so the
# provider-change guard never fires on a fresh session and wipes the messages.
if "active_provider" not in st.session_state:
    _c = next(
        (c for c in st.session_state.chats if c["id"] == st.session_state.current_chat_id),
        st.session_state.chats[0],
    )
    st.session_state.active_provider = _c.get("provider", list(MODELS)[0])
    st.session_state.active_model    = _c.get("model",    MODELS[list(MODELS)[0]][0])

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
st.sidebar.title("⚙️ Settings")

provider = st.sidebar.selectbox("Select Provider", list(MODELS.keys()))
model_name = st.sidebar.selectbox("Select Model", MODELS[provider])

# Reset messages when provider / model switches
if (provider   != st.session_state.active_provider or
        model_name != st.session_state.active_model):
    current_chat()["messages"] = []
    current_chat()["provider"] = provider
    current_chat()["model"]    = model_name
    st.session_state.active_provider = provider
    st.session_state.active_model    = model_name
    save_chats()

st.sidebar.divider()

# ── New Chat ─────────────────────────────────────
if st.sidebar.button("➕  New Chat", use_container_width=True, type="primary"):
    new = make_chat(provider, model_name)
    st.session_state.chats.insert(0, new)
    st.session_state.current_chat_id = new["id"]
    save_chats()
    st.rerun()

st.sidebar.divider()

# ── Chat history grouped by date ─────────────────
groups = group_chats_by_date(st.session_state.chats)

for group_label, group_chats in groups.items():
    if not group_chats:
        continue

    st.sidebar.markdown(f"###### {group_label}")

    for chat in group_chats:
        is_active = chat["id"] == st.session_state.current_chat_id
        col_btn, col_del = st.sidebar.columns([5, 1])

        label = f"**{chat['title']}**" if is_active else chat["title"]
        if col_btn.button(
            label,
            key=f"switch_{chat['id']}",
            use_container_width=True,
            help=f"{chat['provider']} / {chat['model']}",
        ):
            switch_to(chat["id"])
            st.rerun()

        if len(st.session_state.chats) > 1:
            if col_del.button("🗑", key=f"del_{chat['id']}", help="Delete chat"):
                delete_chat(chat["id"])
                st.rerun()

st.sidebar.divider()
st.sidebar.caption(f"💾 History saved to `chat_history.json`")

# ---------------------------------------------------
# MAIN AREA
# ---------------------------------------------------
chat = current_chat()

st.title("🤖 Multi-Model Chatbot")
st.caption(f"▶ {chat['provider']} / {chat['model']}  •  {chat['title']}")

for message in chat["messages"]:
    avatar = USER_AVATAR if message["role"] == "user" else ASSISTANT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------------------------------------------------
# USER INPUT
# ---------------------------------------------------
user_input = st.chat_input("Type your message...")

if user_input:

    # Auto-title on first message
    if chat["title"] == "New Chat":
        chat["title"] = user_input[:40] + ("…" if len(user_input) > 40 else "")

    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(user_input)

    chat["messages"].append({"role": "user", "content": user_input})
    chat["updated_at"] = datetime.now().isoformat()

    llm = load_model(provider, model_name)

    payload = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"(response_variation: {random.randint(1, 999999)})"},
    ]
    for msg in chat["messages"]:
        payload.append({"role": msg["role"], "content": msg["content"]})

    try:
        with st.spinner(f"Thinking with {model_name}..."):
            response = llm.invoke(payload)
        assistant_reply = response.content

        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.write_stream(typewriter(assistant_reply))

        chat["messages"].append({"role": "assistant", "content": assistant_reply})
        chat["updated_at"] = datetime.now().isoformat()

        # ── Save to disk after every successful exchange ──
        save_chats()

    except Exception as exc:
        chat["messages"].pop()
        st.error(f"**{provider} error:** {exc}")
