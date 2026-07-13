# AI Agent Support Assistant

An intelligent AI agent that can answer questions from uploaded policy documents while also triggering structured actions such as checking or updating order status. It is designed as a foundation for future agent capabilities like password changes, receipt printing, and other business workflows.

## Why this project matters

This project shows how AI agents can move beyond simple chat and become practical assistants for real support operations. Instead of only generating text, the agent can combine retrieval over company knowledge with tool-based actions to help users complete tasks. That makes it valuable for:

- faster policy and document lookup
- grounded answers powered by retrieval-augmented generation (RAG)
- action-oriented support workflows
- a foundation for future API-driven automations and internal tools

## What the project does

- uploads and indexes policy documents such as PDFs and text files
- answers questions using a retrieval-augmented generation flow
- acts as an AI agent that can reason over requests and trigger relevant actions
- supports order-related workflows such as checking or updating order status
- provides a simple Streamlit-based interface for chat, file management, and workspace visibility

## Tech stack

- Frontend: Streamlit
- Backend: FastAPI
- AI orchestration: LangChain and LangGraph
- LLM: Groq (Llama model)
- Embeddings: Google Gemini
- Vector search: FAISS
- Data source: local JSON-based order database

## How I built it

1. Built a FastAPI backend with endpoints for chat, file upload, file listing, and order retrieval.
2. Processed uploaded documents into chunks, generated embeddings, and stored them in a FAISS index for semantic search.
3. Connected the LLM to a retrieval pipeline so responses are grounded in the uploaded knowledge base.
4. Added agent-style tool calling so the system can route requests toward structured actions such as order lookups and updates.
5. Designed a Streamlit frontend with a chat experience, sidebar workspace view, and knowledge-base file list.

## Project impact

This project highlights an AI agent architecture that combines knowledge retrieval with action execution. It is a strong example of how an assistant can support both information lookup and workflow automation, with RAG as one of its key capabilities rather than the only focus.

## Screenshots

### Chat experience and knowledge base view

![AI assistant interface](docs/assets/S1.JPG)

### File upload and sidebar organization

![Knowledge base management](docs/assets/S2.JPG)

## Demo

![App preview](https://github.com/pitalsmith/ai-agent-support/blob/75d7a8d209af63424c4e69dc10c45f0843b7efa8/docs/assets/Comp%2012.gif)

## Getting started

```bash
git clone https://github.com/pitalsmith/ai-agent-support.git
cd ai-agent-support
```

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Frontend:

```bash
cd ../frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Make sure to add your API keys in the backend environment before running the app.

