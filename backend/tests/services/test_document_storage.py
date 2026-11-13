from io import BytesIO
from uuid import uuid4
import pytest

from app.services.document_storage import DocumentStorage


@pytest.mark.unit
def test_save_original_pdf(tmp_path) -> None:
    storage = DocumentStorage(tmp_path / "documents")

    owner_id = uuid4()
    document_id = uuid4()
    source = BytesIO(b"%PDF-1.7\ntest document\n%%EOF")

    storage_key = storage.save_original(
        owner_user_id=owner_id,
        document_id=document_id,
        source=source,
    )

    path = storage.get_path(storage_key)

    assert path.exists()
    assert path.read_bytes() == source.getvalue()
    assert storage_key == f"{owner_id}/{document_id}/original.pdf"