# RAG-GenAI-System: Intelligent Document Assistant

### Overview

**RAG-GenAI-System** is a powerful, modular Retrieval-Augmented Generation (RAG) application. It empowers users to upload private documents (PDFs, TXT, DOCX) and engage in a natural, intelligent conversation with them. By leveraging the speed of Groq and the semantic precision of Google Gemini embeddings, this system ensures that the AI's responses are accurate, grounded in your provided documents, and free from hallucinations.

### Tech Stack

* **Frontend:** Streamlit – For rapid, interactive data-driven UI.
* **Backend:** FastAPI – For high-performance, asynchronous API operations.
* **LLM (Generation):** Groq API (using Llama 3) for lightning-fast inference.
* **Embeddings:** Google Gemini (`text-embedding-004`) for high-quality semantic understanding.
* **Orchestration:** LangChain for building the retrieval pipeline.
* **Vector Database:** FAISS – For efficient local similarity search.
* **Deployment:** Render – Automated cloud hosting with CI/CD.

![App Gif](https://github.com/pitalsmith/rag-genai-system/blob/54f16b60ca2e4536af3e9bcc7f024175a8beee93/docs/assets/Ai%20Assistant.gif)

### [Visit the Live RAG AI App here](https://rag-genai-system-1.onrender.com)
### Why This Project?

In a data-heavy environment, standard LLMs often struggle with private or specific documentation. This project bridges that gap by:

* **Grounding AI in Fact:** The AI only answers questions based on the documents you upload.
* **Intelligent Search:** Using cutting-edge embeddings to understand the *meaning* behind your questions, not just keyword matching.
* **Production-Ready Architecture:** Decoupling the frontend (Streamlit) from the backend (FastAPI) to ensure professional, scalable, and manageable code.
* **Total Control:** Features a user-friendly interface to index, manage, and delete documents from your knowledge base instantly.



### How It Works

1. **Ingestion:** Files are uploaded and processed into manageable text chunks.
2. **Vectorization:** Text chunks are transformed into vector embeddings using **Google Gemini**.
3. **Storage:** Embeddings are saved into a **FAISS** vector index for lightning-fast similarity lookups.
4. **Retrieval & Generation:** When a user asks a question, the system finds the most relevant document segments and sends them to **Groq/Llama 3**, which crafts a precise answer based solely on that context.

📸 Screenshots

1. Chat Interface & Knowledge Base Management
A sleek, intuitive chat interface where the AI answers questions grounded in your uploaded documents. The sidebar provides full control over your knowledge base, allowing you to index new files and delete old ones with ease.
![AI Assistant Overview](https://github.com/pitalsmith/rag-genai-system/blob/b9be3422c14ef6ed02dec6bd7a2d88396c6c78f7/docs/assets/S1.JPG)

3. Document Upload & File Management
Easily upload new PDFs, TXT, or DOCX files. The scrollable knowledge base in the sidebar keeps your workspace organized, ensuring your documents are always indexed and ready for retrieval.
![AI Assistant Overview](https://github.com/pitalsmith/rag-genai-system/blob/b9be3422c14ef6ed02dec6bd7a2d88396c6c78f7/docs/assets/S2.JPG)

### How to Run Locally

#### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/rag-genai-system.git
cd rag-genai-system

```

#### 2. Configure Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

```

Create a `.env` file in the `backend/` folder with your API keys:

```text
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_gemini_api_key_here

```

Run the server:

```bash
uvicorn main:app --reload

```

#### 3. Configure Frontend

```bash
cd ../frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

```

### Deployment Note

This project is configured for **Render**. When deploying, ensure you add the following Environment Variables to both your Backend and Frontend (where applicable) in the Render Dashboard:

* `GROQ_API_KEY`
* `GOOGLE_API_KEY`
* `BACKEND_URL` (For the frontend, pointing to your live backend URL)

### Future Enhancements

* [ ] Add support for multi-user session management.
* [ ] Integrate cloud-persistent storage for the FAISS index.
* [ ] Implement source-citation highlighting for better transparency in AI answers.

---

*Created by Peter Atunde*
