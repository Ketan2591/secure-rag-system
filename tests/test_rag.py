from io import BytesIO
import uuid

import pytest

from src.rag_pipeline import (
    ingest_document,
    answer_question,
    format_context,
    get_sources,
)


def unique_user(prefix: str) -> str:
    """
    Create a unique customer ID for each test run so old
    persistent ChromaDB data cannot affect the result.
    """
    return f"{prefix}_{uuid.uuid4().hex}"


def test_complete_rag_pipeline():
    """
    Verify the complete end-to-end RAG flow:

    TXT document
        -> ingestion
        -> chunking
        -> vector storage
        -> retrieval
        -> Groq LLM
        -> grounded answer
        -> source citation
    """

    user_id = unique_user("pytest_rag")

    document_text = (
        "Northstar Technologies Employee Policy\n\n"
        "Employees receive exactly 27 paid leaves every year.\n"
        "The probation period is 5 months.\n"
        "Employees may work remotely for 2 days per week."
    )

    file = BytesIO(document_text.encode("utf-8"))

    ingestion_result = ingest_document(
        file=file,
        filename="rag_test_policy.txt",
        user_id=user_id,
    )

    # Verify ingestion
    assert ingestion_result["filename"] == "rag_test_policy.txt"
    assert ingestion_result["pages_processed"] >= 1
    assert ingestion_result["chunks_created"] >= 1
    assert ingestion_result["chunks_stored"] >= 1

    # Ask a question whose answer exists only in our test document
    result = answer_question(
        question="How many paid leaves do employees receive every year?",
        user_id=user_id,
    )

    # Verify response structure
    assert isinstance(result, dict)
    assert "answer" in result
    assert "sources" in result

    # Verify grounded answer
    assert "27" in result["answer"]

    # Verify source citation
    assert len(result["sources"]) > 0

    assert any(
        source["source"] == "rag_test_policy.txt"
        for source in result["sources"]
    )


def test_unknown_customer_returns_no_documents():
    """
    A customer with no indexed documents must not receive
    information from another customer's workspace.
    """

    user_id = unique_user("pytest_empty_customer")

    result = answer_question(
        question="What is the confidential project codename?",
        user_id=user_id,
    )

    assert result["answer"] == (
        "The requested information was not found "
        "in the uploaded documents."
    )

    assert result["sources"] == []


def test_empty_question_is_rejected():
    """
    Empty questions should fail before retrieval/LLM execution.
    """

    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        answer_question(
            question="   ",
            user_id="pytest_customer",
        )


def test_missing_user_id_is_rejected():
    """
    RAG queries must always belong to a customer workspace.
    """

    with pytest.raises(
        ValueError,
        match="user_id is required",
    ):
        answer_question(
            question="What is the policy?",
            user_id="",
        )


def test_ingestion_without_user_id_is_rejected():
    """
    Documents must never be stored without tenant ownership.
    """

    file = BytesIO(
        b"This document should never be stored."
    )

    with pytest.raises(
        ValueError,
        match="user_id is required",
    ):
        ingest_document(
            file=file,
            filename="invalid.txt",
            user_id="",
        )


def test_source_deduplication():
    """
    Duplicate retrieved chunks from the same source/page
    should produce only one source reference.
    """

    from langchain_core.documents import Document

    documents = [
        Document(
            page_content="First chunk",
            metadata={
                "source": "policy.pdf",
                "page": 1,
            },
        ),
        Document(
            page_content="Second chunk",
            metadata={
                "source": "policy.pdf",
                "page": 1,
            },
        ),
        Document(
            page_content="Third chunk",
            metadata={
                "source": "policy.pdf",
                "page": 2,
            },
        ),
    ]

    sources = get_sources(documents)

    assert len(sources) == 2

    assert {
        "source": "policy.pdf",
        "page": 1,
    } in sources

    assert {
        "source": "policy.pdf",
        "page": 2,
    } in sources


def test_context_contains_source_and_content():
    """
    Retrieved chunks should be formatted with source/page
    metadata before being sent to the LLM.
    """

    from langchain_core.documents import Document

    documents = [
        Document(
            page_content="Annual leave is 27 days.",
            metadata={
                "source": "employee_policy.txt",
                "page": 1,
            },
        )
    ]

    context = format_context(documents)

    assert "employee_policy.txt" in context
    assert "Page: 1" in context
    assert "Annual leave is 27 days." in context