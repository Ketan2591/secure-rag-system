"""
Central place for every setting that's driven by an environment variable --
API keys, DB connection info, which LLM/embedding model to use, chunking
params, all of it. Keeping it all here means nothing further down the stack
(auth, the RAG pipeline, the vector store, etc.) ever hardcodes a value or
reads os.environ directly; it just imports a name from this module.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from .env
load_dotenv(BASE_DIR / ".env")


# 1. LLM PROVIDER & MODEL CONFIGURATION (Single-Point Dynamic Config)

# Preferred active provider: "auto" (Groq -> Gemini -> Mixtral fallback), "groq", "gemini", or "mixtral"
ACTIVE_LLM_PROVIDER = os.getenv("ACTIVE_LLM_PROVIDER", "auto")

# Groq LLM Settings
# No default for the key itself -- it's a secret, so if it's missing we'd
# rather fail loudly (see validate_config below) than silently run with None.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# Google Gemini LLM Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Fallback LLM Models Chain (Groq -> Gemini -> Groq secondary, all currently active models)
LLM_FALLBACK_CHAIN = [
    {"provider": "groq", "model": GROQ_MODEL, "api_key": GROQ_API_KEY},
    {"provider": "gemini", "model": GEMINI_MODEL, "api_key": GEMINI_API_KEY},
    {"provider": "groq", "model": "openai/gpt-oss-20b", "api_key": GROQ_API_KEY},
]

# Read Streamlit secrets fallback if env variables aren't set
if not GROQ_API_KEY:
    try:
        import streamlit as st
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except Exception:
        GROQ_API_KEY = None

if not GEMINI_API_KEY:
    try:
        import streamlit as st
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        GEMINI_API_KEY = None


# 2. VECTOR DATABASE CONFIGURATION (Pinecone Primary + Chroma DB Fallback)

VECTOR_DB_PROVIDER = os.getenv("VECTOR_DB_PROVIDER", "pinecone")

# Pinecone Settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "securerag-index")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

if not PINECONE_API_KEY:
    try:
        import streamlit as st
        PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY")
    except Exception:
        PINECONE_API_KEY = None

# Local ChromaDB Fallback Settings
CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "secure_documents"



# 3. POSTGRESQL DATABASE CONFIGURATION

# These all have sane local-dev defaults, unlike the API keys above --
# a missing Postgres password just means "no password set locally", not
# a broken deployment, so it's fine to fall back quietly here.
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "secure_rag_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")



# 4. EMBEDDINGS & RAG PIPELINE CONFIGURATION

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K_RESULTS = 6


# Checks that at least one LLM API key (Groq or Gemini) is set, since the app can't call any model without one.
# Raises a ValueError with a clear message telling the user to add the missing key if both are empty.
def validate_config():
    if not GROQ_API_KEY and not GEMINI_API_KEY:
        raise ValueError(
            "Neither GROQ_API_KEY nor GEMINI_API_KEY is configured. "
            "Please add GROQ_API_KEY or GEMINI_API_KEY to your .env file or Streamlit secrets."
        )
