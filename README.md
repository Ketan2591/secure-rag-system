# SecureRAG System

SecureRAG System is a multi-tenant Retrieval-Augmented Generation (RAG) application built with Python and Streamlit.

Users can upload PDF, DOCX, or TXT documents and ask questions based on their content. Before documents are embedded and stored, sensitive information is masked. Documents are also separated by customer ID so that one customer cannot retrieve another customer's data.

The application uses local Hugging Face embeddings, ChromaDB for vector storage, and Groq for generating answers from retrieved document context.

## Features

- Upload PDF, DOCX, and TXT documents
- Mask sensitive information before embedding
- Isolate documents by Customer ID
- Generate embeddings locally
- Store document chunks in ChromaDB
- Retrieve relevant document context using semantic search
- Generate grounded answers using Groq
- Display source file and page references
- Ignore instructions found inside uploaded documents
- Automated tests for PII masking, tenant isolation, and the RAG pipeline

## How It Works

```text
Document Upload
      ↓
Text Extraction
      ↓
PII Masking
      ↓
Text Chunking
      ↓
Local Embeddings
      ↓
ChromaDB
      ↓
Customer-Filtered Retrieval
      ↓
Groq LLM
      ↓
Answer + Source References
```

PII masking happens before chunk embeddings are generated, so sensitive values are not intentionally stored as raw text in the vector database.

Each stored chunk also contains a `user_id`. The same ID is used as a metadata filter during retrieval, which keeps customer workspaces separated.

## Security

### PII Masking

Microsoft Presidio and spaCy are used to detect and mask sensitive information.

The application handles values such as:

```text
<PERSON>
<EMAIL_ADDRESS>
<PHONE_NUMBER>
<PASSWORD>
<CLIENT_ID>
<CREDIT_CARD>
<IP_ADDRESS>
```

For example, an email or password detected during document processing is replaced with a protected placeholder before the text reaches the embedding step.

### Customer Isolation

Every chunk stored in ChromaDB is associated with the customer that uploaded it.

Retrieval is restricted using:

```python
filter={"user_id": user_id.strip()}
```

This prevents a query from one customer workspace from retrieving chunks belonging to another customer.

### Grounded Answers

The LLM receives only the document chunks retrieved for the current customer.

If the requested information is not available in the retrieved context, the application returns:

```text
The requested information was not found in the uploaded documents.
```

The prompt also instructs the model not to reconstruct masked information or follow instructions contained inside uploaded documents.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| UI | Streamlit |
| RAG | LangChain |
| LLM | Groq |
| Embeddings | Hugging Face Sentence Transformers |
| Vector Store | ChromaDB |
| PII Detection | Microsoft Presidio |
| NLP | spaCy |
| PDF Processing | PyMuPDF |
| DOCX Processing | python-docx |
| Testing | pytest |

## Project Structure

```text
secure-rag-system/
│
├── src/
│   ├── config.py
│   ├── document_processor.py
│   ├── embeddings.py
│   ├── pii_masker.py
│   ├── rag_pipeline.py
│   ├── text_splitter.py
│   └── vector_store.py
│
├── tests/
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

The local ChromaDB data, `.env`, virtual environment, and cache files are excluded from Git.

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd secure-rag-system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install the spaCy model

```bash
python -m spacy download en_core_web_lg
```

### 5. Configure the API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

A `.env.example` file is included as a reference. The real `.env` file should not be committed.

## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

Then:

1. Enter a Customer ID.
2. Upload one or more supported documents.
3. Click **Process Documents Securely**.
4. Wait for the documents to be indexed.
5. Ask questions in the Secure Document Assistant.
6. Open **View answer sources** to see the source file and page.

## Testing

Run all tests with:

```bash
python -m pytest tests -v
```

The current test suite contains 13 tests:

| Area | Tests |
|---|---:|
| PII Masking | 5 |
| Tenant Isolation | 1 |
| RAG Pipeline | 7 |
| **Total** | **13** |

All 13 tests pass in the current development environment.

The tests cover PII masking, cross-customer isolation, end-to-end document ingestion and question answering, input validation, source handling, and context formatting.

## Notes

This project demonstrates application-level security controls for a RAG system. In a production environment, authentication, authorization, encryption, audit logging, secure secret management, and stronger infrastructure-level tenant isolation would also be required.

## Author

**Ketankumar Prajapat**<br>
**AI/ML & Automation Enthusiast**