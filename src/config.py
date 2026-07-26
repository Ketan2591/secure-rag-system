import os
from pathlib import Path

from dotenv import load_dotenv


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


# API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
    """Validate required application configuration."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. "
            "Please add it to the .env file."
        )