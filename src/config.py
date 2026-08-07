import os
from pathlib import Path

from dotenv import load_dotenv


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables
load_dotenv(BASE_DIR / ".env")


# API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# If runn   ing on Streamlit Cloud, read from Streamlit secrets
if not GROQ_API_KEY:
    try:
        import streamlit as st
        GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
    except Exception:
        GROQ_API_KEY = None


# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "secure_rag_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


# Vector database configuration
CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "secure_documents"

# Embedding configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# RAG configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K_RESULTS = 4


def validate_config():
    """Check if the required API key is available."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Add it to the .env file or Streamlit secrets."
        )