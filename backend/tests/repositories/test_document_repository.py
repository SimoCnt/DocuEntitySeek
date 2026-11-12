import pytest
from sqlalchemy.orm import Session

from app.repositories.document_repository import DocumentRepository


@pytest.mark.integration
def test_create_and_list_documents_for_owner(db_session: Session, user_factory) -> None:
    user = user_factory()
    repository = DocumentRepository(db_session)

    created = repository.create(
        owner_user_id=user.id,
        original_name="disciplinare.pdf",
        category="DISCIPLINARE",
        mime_type="application/pdf",
        size_bytes=1200,
    )

    documents = repository.list_by_owner(user.id)

    assert created.id is not None
    assert len(documents) == 1
    assert documents[0].id == created.id
    assert documents[0].original_name == "disciplinare.pdf"


@pytest.mark.integration
def test_documents_are_isolated_by_owner(db_session: Session, user_factory) -> None:
    user_a = user_factory(email="a@example.com")
    user_b = user_factory(email="b@example.com")
    repository = DocumentRepository(db_session)

    repository.create(
        owner_user_id=user_a.id,
        original_name="private.pdf",
        category="DISCIPLINARE",
        mime_type="application/pdf",
        size_bytes=100,
    )

    documents_b = repository.list_by_owner(user_b.id)

    assert documents_b == []