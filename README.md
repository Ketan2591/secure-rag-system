# SecureRAG - Multi-Tenant Private RAG System

SecureRAG is a Retrieval-Augmented Generation (RAG) system built with Python, Streamlit, LangChain, ChromaDB, and Groq. 

The main goal of this project is to solve two major security challenges in standard RAG implementations:
1. **PII and Sensitive Data Leakage**: Document content is scanned and masked *before* generating embeddings or storing data, preventing sensitive information like phone numbers, emails, passwords, and API keys from being exposed to vector databases or cloud LLMs.
2. **Multi-Tenant Data Isolation**: Document chunks are stored with customer-specific metadata tags (`user_id`). Queries use strict metadata filtering to ensure one user cannot retrieve another user's documents.

---

## Architecture Flow

The system processes documents through a secure pipeline:

```text
Document Upload (PDF, DOCX, TXT)
       ↓
Text Extraction (PyMuPDF / python-docx)
       ↓
PII & Secret Masking (Presidio + spaCy + Regex)
       ↓
Text Chunking (Recursive split with overlap)
       ↓
Local Vector Embeddings (Hugging Face all-MiniLM-L6-v2)
       ↓
ChromaDB Storage (Tagged with user_id metadata)
       ↓
Filtered Similarity Search (filter by current user_id)
       ↓
Grounded QA via Groq LLM (Llama 3.3)
```

---

## Key Features

- **Sensitive Data Masking**: Replaces emails, phone numbers, passwords, credit cards, SSN, Aadhaar, PAN, and API keys with placeholders like `<PHONE_NUMBER>` or `<API_KEY>`.
- **Local Embedding Generation**: Generates 384-dimensional embeddings locally using `all-MiniLM-L6-v2`, so raw text never leaves the local machine.
- **Tenant Isolation**: Every vector chunk is tied to a `user_id` metadata attribute and filtered at query time in ChromaDB.
- **Source Attribution**: Answers include source file names and page numbers for reference.
- **Placeholder Preservation**: System prompt ensures the LLM keeps placeholders intact rather than guessing original sensitive values.
- **Prompt Injection Defense**: Document text is treated strictly as data, ignoring embedded commands inside uploaded files.
- **Streamlit Web Interface**: Multi-page dashboard with authentication, document management, chat history, and settings.
- **Database Tracking**: SQLite database tracks registered users, uploaded documents, and chat history with support for soft deletion.

---

## Tech Stack

- **Frontend**: Streamlit
- **RAG Orchestration**: LangChain
- **LLM**: Groq API (`llama-3.3-70b-versatile`)
- **Embeddings**: Hugging Face Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Database**: ChromaDB
- **PII Detection**: Microsoft Presidio, spaCy (`en_core_web_lg`), Custom Regex
- **Metadata Database**: SQLite
- **Document Processing**: PyMuPDF (`fitz`), `python-docx`
- **Testing**: pytest

---

## Project Structure

```text
secure-rag-system/
├── app.py                      # Main Streamlit router
├── requirements.txt            # Project dependencies
├── setup_database.py           # Database setup script
├── src/
│   ├── auth.py                 # User authentication & hashing
│   ├── config.py               # Application configuration
│   ├── database.py             # SQLite helper functions
│   ├── document_processor.py   # PDF, DOCX, TXT text extractor
│   ├── embeddings.py           # Local embedding loader
│   ├── pii_masker.py           # Presidio and regex masking engine
│   ├── rag_pipeline.py         # Prompt template and Groq LLM chain
│   ├── text_splitter.py        # Text chunking logic
│   ├── vector_store.py         # ChromaDB operations with filtering
│   └── pages/                  # Streamlit pages (dashboard, docs, login, etc.)
└── tests/                      # Automated test suite
    ├── test_isolation.py
    ├── test_masking.py
    └── test_rag.py
```

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Ketan2591/secure-rag-system.git
cd secure-rag-system
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate it:
- **Windows**: `.venv\Scripts\activate`
- **Linux/macOS**: `source .venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### 4. Set up environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser to log in, upload documents, and test the RAG assistant.

---

## Running Tests

Run the pytest suite to verify masking, isolation, and RAG pipelines:

```bash
python -m pytest tests -v
```

---

## Author

**Ketankumar Prajapat**  
*AI & Automation Developer*