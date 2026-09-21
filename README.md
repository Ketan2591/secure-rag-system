# 🛡️ SecureRAG System

SecureRAG is a production-grade, multi-tenant **Retrieval-Augmented Generation (RAG)** application built with Python, Streamlit, LangChain, and a dynamically-selected stack of LLM, vector store, and database providers.

It allows enterprise users to upload **PDF, DOCX, and TXT** documents and perform source-grounded question answering while strictly safeguarding sensitive personal data (PII) and maintaining multi-tenant workspace isolation.

---

## ✨ Key Features & Architecture Highlights

- 🛡️ **Pre-Embedding PII & Secrets Masking**: Automatically detects and replaces sensitive information (SSN, Phone, Email, Passwords, API Keys, Credit Cards, Aadhaar, PAN, Bank Accounts) with protected placeholders *before* vector embeddings are generated or stored.
- 👥 **Strict Multi-Tenant Workspace Isolation**: Assigns a unique `Customer ID` metadata tag to every vector chunk. Vector store queries use a mandatory `filter={"user_id": customer_id}` to prevent cross-tenant data leakage.
- 🧠 **Local Embedding Engine**: Generates 384-dimensional vector embeddings locally using Hugging Face (`all-MiniLM-L6-v2`), ensuring unmasked document content never leaves the secure local server.
- 🤖 **Multi-Provider LLM Failover**: Dynamically routes questions through **Groq** (`openai/gpt-oss-120b`) as the primary model, with automatic failover to **Google Gemini** (`gemini-2.5-flash`) and backup Groq models if a provider rate-limits or is unavailable.
- 🗂️ **Dual Vector Store Backend**: Uses **Pinecone** (cloud) when an API key is configured, and transparently falls back to a local **ChromaDB** store otherwise — no setup required for local development.
- 📚 **Source & Page Attribution**: Every answer includes clickable references displaying the exact source filename and page numbers used for generation.
- 🔐 **Placeholder Preservation**: Instructs the LLM never to guess, decode, or reveal raw sensitive values behind protected placeholders like `<PHONE_NUMBER>` or `<API_KEY>`.
- 🛡️ **Indirect Prompt Injection Defense**: Treats retrieved document chunks strictly as read-only data, ignoring embedded commands or prompt override attempts inside documents.
- 🎨 **Enterprise Multi-Page UI with Light/Dark Theme**: Built with Streamlit featuring a custom CSS design system, user authentication, interactive dashboard, document manager, chat history, profile, and system settings.
- 🗄️ **Dual Database Backend & Soft Deletion**: Uses **PostgreSQL** when configured, falling back to a local **SQLite** database (`secure_rag.db`) automatically — supporting file management, soft deletion, and vector store cleanup safeguards.
- 🧪 **Automated Test Suite**: 20 automated unit & integration tests covering PII masking, multi-tenant isolation, and RAG QA pipelines.

---

## 🏗️ System Architecture

```text
                               ┌───────────────────────────┐
                               │     Document Upload       │
                               │   (PDF, DOCX, TXT Files)  │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │      Text Extraction      │
                               │   (PyMuPDF / python-docx) │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  Sensitive Data & PII     │
                               │        Masking            │
                               │(Presidio + spaCy + Regex) │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │       Text Chunking       │
                               │(LangChain 1000-char/150-ov)│
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │     Local Embeddings      │
                               │ (HF all-MiniLM-L6-v2)     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Pinecone / Chroma Vector DB│
                               │  + user_id Metadata Tag   │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Customer-Filtered Search  │
                               │ filter={"user_id": CUS_X} │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │    Protected Context      │
                               │   + System Guardrails     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  Groq / Gemini LLM        │
                               │  (Dynamic Failover)       │
                               │    Source-Grounded QA     │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │ Grounded Answer + Source  │
                               │     Filename & Page #     │
                               └───────────────────────────┘
```

---

## 🛡️ Security & Privacy Engine

### 1. PII & Secrets Masking Rules

SecureRAG combines **Microsoft Presidio**, **spaCy**, and custom **Regex rules** to mask sensitive entities prior to vector indexing:

| Category | Detected Entity | Protected Placeholder |
|---|---|---|
| **Personal Info** | Person Name | `<PERSON>` |
| **Contact** | Email Address | `<EMAIL_ADDRESS>` |
| **Contact** | Phone Number | `<PHONE_NUMBER>` |
| **Identity** | US Social Security Number | `<SSN>` |
| **Identity** | Indian Aadhaar Number | `<AADHAAR_NUMBER>` |
| **Identity** | Indian PAN Number | `<PAN_NUMBER>` |
| **Financial** | Credit / Debit Card | `<CREDIT_CARD>` |
| **Financial** | Bank Account Number | `<BANK_ACCOUNT>` |
| **Financial** | IBAN Code | `<IBAN_CODE>` |
| **Network** | IP Address | `<IP_ADDRESS>` |
| **Location** | Physical Location / Address | `<LOCATION>` |
| **Security** | Passwords / PWD | `<PASSWORD>` |
| **Security** | API Keys | `<API_KEY>` |
| **Security** | Client Secrets | `<SECRET>` |
| **Security** | OAuth Access Tokens | `<ACCESS_TOKEN>` |
| **Security** | Client IDs | `<CLIENT_ID>` |

#### Example Transformation:
```text
Raw Text:    John Doe's phone number is +91 9876543210 and API key is api_key: 99a88b77c
Masked Text: <PERSON>'s phone number is <PHONE_NUMBER> and API key is api_key: <API_KEY>
```

---

## 👥 Multi-Tenant Isolation

In a shared SaaS environment, every document chunk stored in the vector database is bound to the uploading customer's `user_id`:

```python
# Ingestion: Injected metadata tag
metadata["user_id"] = current_user_id

# Retrieval: Enforced database query filter
results = vector_store.similarity_search(
    query=query,
    k=top_k,
    filter={"user_id": current_user_id}
)
```

This guarantees **Customer B can NEVER retrieve document chunks indexed by Customer A**.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.12 | Core backend application logic |
| **Web Interface** | Streamlit | Responsive multi-page web interface |
| **Framework** | LangChain | RAG pipeline orchestration |
| **LLM Provider** | Groq (`gpt-oss-120b`) + Google Gemini (`gemini-2.5-flash`) | High-speed LLM inference with automatic failover |
| **Embedding Model** | Hugging Face (`all-MiniLM-L6-v2`) | Local 384-d vector embeddings |
| **Vector Database** | Pinecone (cloud) with local ChromaDB fallback | Persistent, multi-tenant vector store |
| **PII Anonymizer** | Microsoft Presidio + spaCy | Named Entity Recognition & Masking |
| **Metadata DB** | PostgreSQL with local SQLite fallback | User authentication & file tracking |
| **Document Parsers**| PyMuPDF (`fitz`), `python-docx` | PDF and Word text extraction |
| **Testing** | pytest | Automated test suite |

---

## 📁 Project Directory Structure

```text
secure-rag-system/
│
├── data/                       # Local databases (Git ignored, used when Pinecone/PostgreSQL aren't configured)
│   ├── chroma_db/              # Local ChromaDB vector store fallback
│   └── secure_rag.db           # Local SQLite metadata & auth storage fallback
│
├── src/                        # Application source code
│   ├── __init__.py
│   ├── assets/                 # Static assets (favicon, etc.)
│   ├── auth.py                 # User login, registration, & password hashing
│   ├── config.py               # Global system configuration & environment variables
│   ├── database.py             # PostgreSQL/SQLite DB manager (Users, Files, History)
│   ├── document_processor.py   # PDF, DOCX, TXT document parser
│   ├── embeddings.py           # Local Hugging Face embedding loader
│   ├── pii_masker.py           # Presidio + spaCy + Regex PII masking engine
│   ├── rag_pipeline.py         # Multi-provider LLM RAG orchestration & failover
│   ├── text_splitter.py        # Recursive character text chunking
│   ├── vector_store.py         # Pinecone/ChromaDB CRUD & multi-tenant isolation search
│   └── pages/                  # Streamlit Multi-Page Views
│       ├── dashboard.py        # Interactive Chat & Upload workspace
│       ├── documents.py        # Document manager with file management & soft deletion
│       ├── history.py          # Complete session chat history view
│       ├── icons.py            # Inline SVG icon set used across the UI
│       ├── login.py            # User authentication login view
│       ├── profile.py          # User workspace profile & Customer ID view
│       ├── register.py         # New user registration view
│       ├── settings.py         # Security rules & vector store configuration view
│       └── styles.py           # Custom CSS design system (light/dark theme)
│
├── scripts/                    # Standalone maintenance & debugging scripts
│   ├── diagnose_retrieval.py   # Inspect DB documents & test sample retrieval queries
│   ├── force_reindex.py        # Delete and re-ingest a single document for a customer
│   └── inspect_user_vectors.py # Inspect a customer's raw vectors in the vector store
│
├── tests/                      # Automated test suite
│   ├── __init__.py
│   ├── test_isolation.py       # Multi-tenant cross-customer isolation tests
│   ├── test_masking.py         # Presidio & Regex PII masking tests
│   └── test_rag.py             # End-to-end RAG pipeline & QA tests
│
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusion rules
├── app.py                      # Streamlit application entry point & router
├── LICENSE                     # MIT License
├── pyrightconfig.json          # Python type checker config
├── README.md                   # Project documentation
└── requirements.txt            # Dependency list
```

---

## 🚀 Quick Start & Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Ketan2591/secure-rag-system.git
cd secure-rag-system
```

### 2. Create and Activate Virtual Environment

```bash
# Create environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies & spaCy Language Model

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory. Only `GROQ_API_KEY` is required to get started — everything else is optional and falls back automatically:

```env
# Required: at least one LLM provider key
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Optional: Gemini fallback LLM
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Pinecone (falls back to local ChromaDB if not set)
PINECONE_API_KEY=your_pinecone_api_key_here

# Optional: PostgreSQL (falls back to local SQLite if not set)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=secure_rag_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

*(You can obtain a free Groq API key from [console.groq.com](https://console.groq.com/) and a free Gemini API key from [aistudio.google.com](https://aistudio.google.com/))*

---

## ▶️ Running the Application

Launch the Streamlit web dashboard:

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`:
1. **Register** a new account or **Login**.
2. Upload your PDF, DOCX, or TXT documents in the **Dashboard**.
3. Click **Process & Index Documents**.
4. Ask questions in the **Secure Assistant** chat!

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:

```bash
python -m pytest tests -v
```

### Test Results Summary:

```text
 20 passed.
```

| Test Suite | Total Tests | Status |
|---|---:|---|
| Sensitive Data & PII Masking | 11 | ✅ PASS |
| Tenant Multi-Isolation | 1 | ✅ PASS |
| End-to-End RAG QA Pipeline | 8 | ✅ PASS |
| **Overall** | **20** | **✅ PASS** |

---

## 📜 License & Security Disclaimer

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute.

It demonstrates enterprise-grade security concepts for multi-tenant RAG applications. Production deployments should complement these controls with infrastructure-level encryption at rest, secure key management (KMS), rate limiting, and network firewalls.

---

## 👤 Author

**Ketankumar Prajapat**  
*AI & Automation Developer*
