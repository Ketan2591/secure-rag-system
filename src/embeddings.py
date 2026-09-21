"""
Loads the sentence-transformer embedding model we use to turn text into
vectors. It's a local HuggingFace model rather than a hosted API, which
matters here specifically: document content (even after masking) never has
to leave the machine just to get embedded. Cached so we only pay the model
load cost once per process.
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL


# Loads the HuggingFace embedding model and keeps it cached (lru_cache) so it is only loaded once per process, not on every call.
# The model runs fully on the local machine, so document text never has to be sent to an external API just to get embedded.
@lru_cache(maxsize=1)
def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )