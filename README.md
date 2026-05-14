# 🤖 PrimeMind — Multi-Model Chatbot

A conversational AI chatbot built with **Streamlit** and **LangChain** that lets you switch between multiple AI providers and models from a single, clean interface — with full persistent chat history that survives page refreshes.

---

## ✨ Features

- 🔀 **Multi-provider support** — OpenAI, Google Gemini, Groq, and Ollama in one app
- 🧠 **Persistent memory** — all conversations saved to `chat_history.json` and restored on refresh
- 💬 **Multi-chat management** — create, switch between, and delete independent conversations
- 📅 **Date-grouped sidebar** — chats organized by Today, Yesterday, Last 7 days, and Older
- ✍️ **Typewriter effect** — responses stream character-by-character for a natural feel
- 🏷️ **Auto-titling** — each chat is automatically named from your first message
- ♻️ **Cached model loading** — model objects are reused across messages for lower latency
- 🛡️ **Error handling with rollback** — failed API calls never corrupt your chat history

---

## 🧩 Supported Providers & Models

| Provider | Models |
|----------|--------|
| **OpenAI** | `gpt-3.5-turbo`, `gpt-4.1` |
| **Gemini** | `gemini-2.5-pro`, `gemini-2.5-flash` |
| **Groq** | `llama-3.1-8b-instant`, `llama-3.3-70b-versatile` |
| **Ollama** | `gemma3`, `llama3.1` |

---

## 📁 Project Structure

```
multi_model_chatbot/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .env                 # API keys (create this — not committed)
├── chat_history.json    # Auto-generated persistent chat store
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/multi-model-chatbot.git
cd multi-model-chatbot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API keys

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...
```

> Ollama runs locally and requires no API key (see [Ollama setup](#ollama-local-setup) below).

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

---

## 🖥️ Ollama Local Setup

Ollama lets you run open-source models fully offline.

```bash
# Install Ollama
# → https://ollama.com/download

# Pull models
ollama pull gemma3
ollama pull llama3.1

# Start the server (runs on localhost:11434)
ollama serve
```

Once running, select **Ollama** as the provider in the sidebar — no API key needed.

---

## 🔐 Environment Variables

| Variable | Provider | Where to get it |
|----------|----------|-----------------|
| `OPENAI_API_KEY` | OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) |
| `GOOGLE_API_KEY` | Gemini | [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `GROQ_API_KEY` | Groq | [console.groq.com](https://console.groq.com/keys) |

---

## 💾 Persistent Chat History

All conversations are automatically saved to `chat_history.json` in the project folder after every reply. On the next visit — even after closing the browser or restarting the server — your full chat history is restored exactly as you left it.

```json
{
  "current_chat_id": "uuid...",
  "chats": [
    {
      "id": "uuid...",
      "title": "How do I reverse a list in Python?",
      "provider": "Groq",
      "model": "llama-3.3-70b-versatile",
      "created_at": "2025-05-13T10:00:00",
      "updated_at": "2025-05-13T10:04:22",
      "messages": [
        { "role": "user", "content": "..." },
        { "role": "assistant", "content": "..." }
      ]
    }
  ]
}
```

> Add `chat_history.json` to your `.gitignore` to avoid committing private conversations.

---

## 🏗️ Architecture

```
User message
     │
     ▼
Sidebar config (provider + model)
     │
     ▼
load_model()  ←── @st.cache_resource (reuses object across reruns)
     │
     ▼
llm.invoke(payload)   ←── LangChain unified interface
     │
     ├── ChatOpenAI
     ├── ChatGoogleGenerativeAI
     ├── ChatGroq
     └── ChatOllama
     │
     ▼
typewriter()  ←── streams reply character by character
     │
     ▼
save_chats()  ←── writes chat_history.json to disk
```

---

## 📦 Dependencies

```
streamlit>=1.35.0
python-dotenv>=1.0.0
langchain-openai>=0.1.0
langchain-google-genai>=1.0.0
langchain-groq>=0.1.0
langchain-ollama>=0.1.0
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🛠️ Customisation

**Add a new provider** — extend the `MODELS` dict and add a branch in `load_model()`:

```python
MODELS = {
    ...
    "Mistral": ["mistral-large-latest", "mistral-small-latest"],
}

def load_model(provider, model_name):
    ...
    elif provider == "Mistral":
        from langchain_mistralai import ChatMistralAI
        return ChatMistralAI(model=model_name, api_key=os.getenv("MISTRAL_API_KEY"))
```

**Change the assistant persona** — edit the `SYSTEM_PROMPT` constant at the top of `app.py`.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
