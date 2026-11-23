"""Test unitari del provider S3 senza effettuare richieste verso un cloud."""
from io import BytesIO
from uuid import uuid4
import pytest
from app.services.document_storage import S3DocumentStorage
from app.services.pdf_content_response import _parse_range, build_pdf_response


class FakeS3Client:
    def __init__(self):
        self.objects = {}
    def upload_fileobj(self, source, bucket, key, ExtraArgs=None):
        self.objects[(bucket, key)] = source.read()
    def head_object(self, *, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise FakeNotFound()
        return {"ContentLength": len(self.objects[(Bucket, Key)])}
    def get_object(self, *, Bucket, Key, Range=None):
        if (Bucket, Key) not in self.objects:
            raise FakeNotFound()
        data = self.objects[(Bucket, Key)]
        if Range:
            start, end = Range.removeprefix("bytes=").split("-", 1)
            data = data[int(start):int(end) + 1 if end else None]
        return {"Body": BytesIO(data)}
    def delete_object(self, *, Bucket, Key):
        self.objects.pop((Bucket, Key), None)


class FakeNotFound(Exception):
    response = {"Error": {"Code": "NoSuchKey"}}


def test_s3_upload_download_and_cleanup(tmp_path):
    client = FakeS3Client()
    storage = S3DocumentStorage(tmp_path, bucket="private", client=client)
    owner, document = uuid4(), uuid4()
    data = b"%PDF-1.7\nTest PDF\n%%EOF"
    key = storage.save_original(owner_user_id=owner, document_id=document, source=BytesIO(data))
    assert storage.get_size(key) == len(data)
    with storage.materialize(key) as path:
        assert path.read_bytes() == data
        extracted_path = path
    assert not extracted_path.exists()
    storage.delete(key)
    with pytest.raises(FileNotFoundError):
        storage.get_size(key)


def test_read_legacy_file_when_not_in_s3(tmp_path):
    storage = S3DocumentStorage(tmp_path, bucket="private", client=FakeS3Client())
    owner, document = uuid4(), uuid4()
    key = f"{owner}/{document}/original.pdf"
    path = storage.get_path(key)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"%PDF-1.7 legacy")
    assert storage.get_size(key) == len(path.read_bytes())
    with storage.materialize(key) as temp_path:
        assert temp_path.read_bytes() == path.read_bytes()
    assert path.exists()


def test_byte_range_validation():
    assert _parse_range("bytes=0-3", 10) == (0, 3)
    assert _parse_range("bytes=5-", 10) == (5, 9)
    assert _parse_range("bytes=-4", 10) == (6, 9)
    with pytest.raises(ValueError):
        _parse_range("bytes=999-", 10)
    with pytest.raises(ValueError):
        _parse_range("bytes=0-1,5-6", 10)
