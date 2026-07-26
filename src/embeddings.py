from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Load and cache the embedding model.

    The model runs locally, so document content does not need
    to be sent to an external embedding API.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )