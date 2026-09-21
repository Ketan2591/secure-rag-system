from io import BytesIO
import uuid

import pytest

from src.rag_pipeline import (
    ingest_document,
    answer_question,
    format_context,
    get_sources,
)


# Builds a fresh, random customer ID for each test run so leftover data from a previous test run in ChromaDB never affects the result.
def unique_user(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


# Runs the full RAG flow end to end on a real TXT document: ingest, chunk, store, retrieve, ask the LLM, and check the answer and its source citation.
def test_complete_rag_pipeline():
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


# Checks that a brand new customer with no uploaded documents gets the standard "not found" answer instead of leaking another customer's data.
def test_unknown_customer_returns_no_documents():
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


# Checks that a blank/whitespace-only question raises a ValueError immediately, before any retrieval or LLM call happens.
def test_empty_question_is_rejected():
    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        answer_question(
            question="   ",
            user_id="pytest_customer",
        )


# Checks that asking a question with an empty user_id raises a ValueError, since every query must belong to some customer's workspace.
def test_missing_user_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="user_id is required",
    ):
        answer_question(
            question="What is the policy?",
            user_id="",
        )


# Checks that uploading a document with an empty user_id raises a ValueError, since a document must never be stored without an owner.
def test_ingestion_without_user_id_is_rejected():
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


# Checks that when several chunks come from the same file and page, get_sources collapses them into a single source entry instead of duplicates.
def test_source_deduplication():
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


# Checks that format_context includes the source filename, page number, and the actual chunk text in the string sent to the LLM.
def test_context_contains_source_and_content():
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


# Uploads two documents with different codenames and checks that passing doc_name to answer_question strictly returns that document's own answer, not the other one's.
def test_doc_name_filtering():
    user_id = unique_user("pytest_doc_name_filter")

    file_a = BytesIO(b"Alpha document project codename is RedDragon.")
    file_b = BytesIO(b"Beta document project codename is BlueOcean.")

    ingest_document(file=file_a, filename="alpha.txt", user_id=user_id)
    ingest_document(file=file_b, filename="beta.txt", user_id=user_id)

    res_alpha = answer_question(
        question="What is the project codename?",
        user_id=user_id,
        doc_name="alpha.txt",
    )
    assert isinstance(res_alpha, dict)
    assert "RedDragon" in res_alpha["answer"]

    res_beta = answer_question(
        question="What is the project codename?",
        user_id=user_id,
        doc_name="beta.txt",
    )
    assert isinstance(res_beta, dict)
    assert "BlueOcean" in res_beta["answer"]
