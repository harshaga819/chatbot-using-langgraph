# Agentic RAG Chatbot — Multi-Tool AI Assistant

A conversational AI assistant that goes beyond static document Q&A. Built with **LangGraph**, it can hold a normal conversation, answer questions from an uploaded PDF or any website, pull live stock prices, and search the web — automatically deciding which capability to use based on what the user asks. Conversations persist across sessions, with support for multiple independent chat threads.

## Features

- **Conversational core** — handles open-ended chat, not just document Q&A, using an LLM served through Groq (Llama 3.3 70B).
- **PDF chat** — upload a PDF per chat thread and ask questions grounded in its actual content.
- **Website chat** — provide any URL and converse with the page's content the same way.
- **Real-time tools**
  - Web search (DuckDuckGo) for questions beyond any uploaded document.
  - Live stock price lookup (Alpha Vantage) for a given ticker symbol.
- **Persistent multi-thread memory** — each conversation is checkpointed to SQLite, so users can create multiple chats, switch between them, and resume any thread with full history intact.
- **Streaming responses** — assistant replies stream live in the UI.

## Tech Stack

| Layer | Tools |
|---|---|
| Orchestration | LangGraph (`StateGraph`, `ToolNode`, `tools_condition`) |
| LLM | Groq — Llama 3.3 70B (`langchain_groq`) |
| Embeddings | Hugging Face — `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Store | FAISS |
| Document Loading | `PyPDFLoader`, `WebBaseLoader` |
| Persistence | SQLite (`langgraph.checkpoint.sqlite.SqliteSaver`) |
| Frontend | Streamlit |
| Search Tool | DuckDuckGo Search |
| Stock Data | Alpha Vantage API |

## Architecture

```
                ┌─────────────┐
   User Input → │    chat     │ ← LLM decides: answer directly OR call a tool
                └──────┬──────┘
                       │  (tool call requested)
                       ▼
                ┌─────────────┐
                │    tools    │  → rag_tool | search_tool | get_stock_price
                └──────┬──────┘
                       │
                       ▼
                back to chat node → final response to user
```

The graph has two nodes — `chat` and `tools` — connected with a conditional edge (`tools_condition`). The LLM decides on every turn whether a tool call is needed; if so, control passes to the `tools` node and back to `chat` to produce the final answer. All conversation state is checkpointed per `thread_id`, so each chat session can be paused and resumed independently.

## Project Structure

```
.
├── backend.py             # LangGraph graph definition, state, and checkpointing
├── config.py               # LLM and embeddings configuration
├── frontend.py              # Streamlit UI: chat, sidebar, PDF/website upload
├── retriever_manager.py     # PDF and website ingestion, chunking, FAISS retrievers
├── tools.py                 # Tool definitions: RAG, web search, stock price
└── chatbot_database.db      # SQLite checkpoint store (created at runtime)
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/harshaga819/agentic-rag-chatbot.git
cd agentic-rag-chatbot
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
ALPHAVANTAGE_API_KEY=your_alphavantage_api_key
```

- **GROQ_API_KEY** — required for the LLM (Llama 3.3 70B via Groq).
- **HUGGINGFACEHUB_API_TOKEN** — required for generating embeddings used in FAISS retrieval.
- **ALPHAVANTAGE_API_KEY** — required for the stock price tool.

### 4. Run the app

```bash
streamlit run frontend.py
```

The app will open in your browser, typically at `http://localhost:8501`.

## Usage

1. **Start a new chat** from the sidebar, or continue an existing one from your conversation history.
2. **Upload a PDF** using the sidebar uploader to enable document Q&A for that thread.
3. **Click "Chat with website"** and paste a URL to enable website Q&A for that thread.
4. **Ask anything** — general questions, questions about the uploaded content, stock prices (e.g., "What's the current price of AAPL?"), or anything requiring a web search. The assistant decides on its own whether to answer directly, retrieve from your document/website, or call a tool.

## Notes

- Each chat thread has its own retriever — a PDF or website ingested in one thread is not available in another.
- Conversation history is stored locally in `chatbot_database.db` via SQLite checkpointing.

## Possible Future Improvements

- Support multiple documents/websites per thread.
- Add citation/source highlighting for retrieved answers.
- Deploy with a hosted vector store for scalability beyond local FAISS.
- Add authentication for multi-user deployments.

## License

This project is open source and available under the MIT License.
