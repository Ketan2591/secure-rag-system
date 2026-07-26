from langchain_core.documents import Document

from src.vector_store import add_documents, search_documents


def test_customer_data_isolation():
    """
    Verify that one customer cannot retrieve another customer's data.
    """

    customer_a = f"pytest_customer_a"
    customer_b = f"pytest_customer_b"

    secret_a = "ALPHA_PRIVATE_PROJECT_XQZ987"
    secret_b = "BETA_PRIVATE_PROJECT_LMN456"

    # Store Customer A's private document
    document_a = Document(
        page_content=f"Customer A confidential project code is {secret_a}.",
        metadata={
            "source": "customer_a_private.txt",
            "page": 1,
        },
    )

    # Store Customer B's private document
    document_b = Document(
        page_content=f"Customer B confidential project code is {secret_b}.",
        metadata={
            "source": "customer_b_private.txt",
            "page": 1,
        },
    )

    add_documents([document_a], customer_a)
    add_documents([document_b], customer_b)

    # Customer A searches for its own secret
    results_a = search_documents(
        query=secret_a,
        user_id=customer_a,
        k=5,
    )

    assert len(results_a) > 0

    customer_a_content = " ".join(
        document.page_content for document in results_a
    )

    assert secret_a in customer_a_content

    # Customer B tries to search for Customer A's secret
    results_b = search_documents(
        query=secret_a,
        user_id=customer_b,
        k=5,
    )

    customer_b_content = " ".join(
        document.page_content for document in results_b
    )

    # Critical security assertion
    assert secret_a not in customer_b_content

    # Also verify returned documents belong only to Customer B
    for document in results_b:
        assert document.metadata.get("user_id") == customer_b