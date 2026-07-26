# 🔐 SecureRAG System

SecureRAG is a secure, multi-tenant **Retrieval-Augmented Generation (RAG)** application built with Python and Streamlit.

It allows users to upload PDF, DOCX, and TXT documents and ask questions based on their content while protecting sensitive information and maintaining strict isolation between customer workspaces.

Before document content is embedded or stored, sensitive information is detected and replaced with protected placeholders. Each document chunk is also associated with a Customer ID so that one customer's queries cannot retrieve another customer's data.

The application uses **local Hugging Face embeddings**, **ChromaDB** for vector storage, and **Groq** for generating source-grounded answers from retrieved document context.

---

## ✨ Features

- 📄 Upload PDF, DOCX, and TXT documents
- 🛡️ Mask PII and sensitive information before embedding
- 👤 Isolate documents using Customer ID based tenant separation
- 🧠 Generate document embeddings locally
- 🗄️ Store protected document chunks in ChromaDB
- 🔍 Retrieve relevant context using semantic search
- 🤖 Generate grounded answers using Groq
- 📚 Display source file and page references
- 🔐 Preserve protected placeholders instead of revealing sensitive values
- 🚫 Ignore instructions embedded inside uploaded documents
- 💬 Interactive Secure Document Assistant
- 🎨 Professional Streamlit interface
- 🧪 Automated tests for masking, tenant isolation, and the RAG pipeline

---

## 🏗️ Architecture

```text
Document Upload
      ↓
Text Extraction
      ↓
Sensitive Data / PII Masking
      ↓
Text Chunking
      ↓
Local Embeddings
      ↓
ChromaDB + user_id Metadata
      ↓
Customer-Filtered Retrieval
      ↓
Protected Document Context
      ↓
Groq LLM
      ↓
Grounded Answer + Source References
```

Sensitive information is masked **before chunk embeddings are generated**, helping prevent raw sensitive values from being intentionally stored in the vector database.

Each stored chunk contains a `user_id`. The same identifier is applied as a metadata filter during retrieval, keeping customer workspaces isolated.

---

## 🔐 Security

### PII & Sensitive Data Masking

SecureRAG uses **Microsoft Presidio**, **spaCy**, and custom detection rules to identify and mask sensitive information before embedding and storage.

Protected information includes:

```text
Person              → <PERSON>
Email Address       → <EMAIL_ADDRESS>
Phone Number        → <PHONE_NUMBER>
Password            → <PASSWORD>
Client ID           → <CLIENT_ID>
Credit Card         → <CREDIT_CARD>
IP Address          → <IP_ADDRESS>
Location            → <LOCATION>
API Key             → <API_KEY>
Secret              → <SECRET>
Access Token        → <ACCESS_TOKEN>
Bank Account        → <BANK_ACCOUNT>
Aadhaar Number      → <AADHAAR_NUMBER>
PAN Number          → <PAN_NUMBER>
IBAN                → <IBAN_CODE>
US SSN              → <SSN>
```

For example:

```text
Phone: +91 9876543210
```

is transformed before embedding into a protected representation such as:

```text
Phone: <PHONE_NUMBER>
```

The original sensitive value is therefore not intentionally passed to the embedding or RAG generation stages.

### Protected Answers

If a user asks for sensitive information that exists in the document, SecureRAG preserves the protected placeholder instead of attempting to reconstruct the original value.

Example:

```text
Question:
What is the person's phone number?

Answer:
The person's phone number is <PHONE_NUMBER>.
```

Similarly:

```text
Email    → <EMAIL_ADDRESS>
Password → <PASSWORD>
API Key  → <API_KEY>
```

The LLM is explicitly instructed never to guess, reconstruct, infer, decode, or reveal the original value represented by a protected placeholder.

---

## 👥 Tenant Isolation

Every document chunk stored in ChromaDB is associated with the Customer ID that uploaded it.

Retrieval is restricted using customer-specific metadata filtering:

```python
filter={
    "user_id": user_id.strip()
}
```

This prevents a query from one customer workspace from retrieving document chunks belonging to another customer.

For example:

```text
Customer A
    ↓
Documents A
    ↓
user_id = customer_a

Customer B
    ↓
Documents B
    ↓
user_id = customer_b
```

A query from `customer_b` cannot retrieve chunks stored for `customer_a`.

---

## 📚 Grounded Answers

The LLM receives only the document chunks retrieved from the active customer workspace.

SecureRAG is instructed to:

- Answer only from provided document context
- Avoid using outside knowledge to invent answers
- Preserve protected placeholders
- Never reconstruct masked sensitive information
- Ignore instructions embedded inside uploaded documents
- Return a fixed fallback when the requested information is unavailable

Fallback response:

```text
The requested information was not found in the uploaded documents.
```

This helps reduce hallucination and keeps responses grounded in the customer's indexed documents.

---

## 🛡️ Prompt Injection Protection

Uploaded document content is treated as **data, not instructions**.

The RAG system explicitly instructs the LLM to ignore commands or instructions that may appear inside retrieved documents.

This provides an application-level defense against document-based prompt injection attempts.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| UI | Streamlit |
| RAG Framework | LangChain |
| LLM | Groq |
| Embeddings | Hugging Face Sentence Transformers |
| Vector Store | ChromaDB |
| PII Detection | Microsoft Presidio |
| NLP | spaCy |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| Testing | pytest |

---

## 📁 Project Structure

```text
secure-rag-system/
│
├── data/
│   └── chroma_db/              # Local vector database (Git ignored)
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── pii_masker.py
│   ├── rag_pipeline.py
│   ├── text_splitter.py
│   └── vector_store.py
│
├── tests/
│   ├── __init__.py
│   ├── test_isolation.py
│   ├── test_masking.py
│   └── test_rag.py
│
├── .env.example
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

The following local or sensitive files are excluded from Git:

```text
.env
.venv/
data/chroma_db/
__pycache__/
.pytest_cache/
```

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd secure-rag-system
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the spaCy Model

```bash
python -m spacy download en_core_web_lg
```

### 5. Configure the Groq API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

A `.env.example` file is included as a reference.

> Never commit your real `.env` file or API key to GitHub.

---

## ▶️ Running the Application

Start SecureRAG using:

```bash
streamlit run app.py
```

Then:

1. Enter a **Customer ID**.
2. Upload one or more PDF, DOCX, or TXT documents.
3. Click **Process Documents Securely**.
4. Sensitive information is masked.
5. Protected document chunks are embedded and indexed.
6. Ask questions using the **Secure Document Assistant**.
7. Open **View answer sources** to inspect source file and page references.

---

## 🧪 Testing

Run the complete automated test suite:

```bash
python -m pytest tests -v
```

Current test suite:

| Area | Tests | Status |
|---|---:|---|
| Sensitive Data / PII Masking | 11 | ✅ PASS |
| Tenant Isolation | 1 | ✅ PASS |
| RAG Pipeline | 7 | ✅ PASS |
| **Total** | **19** | **✅ PASS** |

### Masking Tests

The masking tests verify protection of:

- Email addresses
- Phone numbers
- Passwords
- Client IDs
- Multiple PII values
- API keys
- Client secrets
- Access tokens
- Bank account numbers
- Aadhaar numbers
- PAN numbers

### RAG & Security Tests

The remaining tests verify:

- Cross-customer data isolation
- Complete ingestion → retrieval → answer pipeline
- Unknown customer isolation
- Empty-question validation
- Missing Customer ID validation
- Ingestion validation
- Source deduplication
- Context formatting

Current result:

```text
================ 19 passed ================
```

---

## ✅ Verified Security Behavior

End-to-end testing confirms that sensitive document values are returned as protected placeholders.

Examples:

```text
Phone Number → <PHONE_NUMBER>

Email Address → <EMAIL_ADDRESS>

Person Name → <PERSON>
```

Normal non-sensitive document information remains queryable.

Example:

```text
Question:
How many paid leaves are allowed?

Answer:
SecureTech provides 24 paid leaves to every employee per year.
```

This demonstrates that SecureRAG can protect sensitive fields while still allowing useful document-based question answering.

---

## 🔒 Security Design Principles

SecureRAG follows several important application-level security principles:

1. **Mask before embedding** — sensitive values are protected before vector generation.
2. **Tenant-filtered retrieval** — every retrieval operation is scoped to the active Customer ID.
3. **Grounded generation** — answers are generated only from retrieved document context.
4. **Protected placeholders** — masked values are never intentionally reconstructed.
5. **Document instructions are untrusted** — retrieved document content is treated as data.
6. **Secrets stay outside Git** — API keys and local databases are excluded from version control.

---

## Future Improvements

Potential production enhancements include:

- User authentication
- Role-Based Access Control (RBAC)
- Database-backed user management
- Encryption at rest
- Advanced secret management
- Audit logging
- Rate limiting
- Document deletion and lifecycle management
- Conversation history
- Docker containerization
- Cloud deployment
- RAG evaluation and observability
- Stronger infrastructure-level tenant isolation

---

## Security Note

SecureRAG is a prototype demonstrating security controls for a multi-tenant RAG application.

PII detection and pattern-based masking cannot guarantee detection of every possible form of sensitive information. A production deployment should additionally use authentication, authorization, encryption, secure secret management, auditing, infrastructure isolation, monitoring, and appropriate data-governance controls.

---

## Author

**Ketankumar Prajapat**<br>
**AI/ML & Automation Enthusiast**