import pytest
from sqlalchemy.orm import Session

from app.pipeline.models import PreparedDocumentPage
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.document_repository import DocumentRepository


@pytest.mark.integration
def test_replace_document_pages(db_session: Session, user_factory) -> None:
    user = user_factory()

    document = DocumentRepository(db_session).create(
        owner_user_id=user.id,
        original_name="document.pdf",
        category="DISCIPLINARE",
        mime_type="application/pdf",
        size_bytes=100,
    )

    repository = DocumentPageRepository(db_session)

    repository.replace_for_document(
        document_id=document.id,
        pages=(
            PreparedDocumentPage(page_number=1, text="ABC", global_start=0, global_end=3),
            PreparedDocumentPage(page_number=2, text="DEF", global_start=5, global_end=8),
        )
    )

    pages = repository.list_for_document(document.id)

    assert len(pages) == 2
    assert pages[0].page_number == 1
    assert pages[0].extracted_text == "ABC"
    assert pages[1].global_start == 5