"""Accesso autenticato al PDF originale, compatibile con richieste HTTP Range."""
import re
from collections.abc import Iterator
from fastapi.responses import Response, StreamingResponse
from app.core.exceptions import DocumentStorageError
from app.services.document_storage import DocumentStorage


def _parse_range(value: str | None, size: int) -> tuple[int, int] | None:
    """Parse a supported single HTTP Range header against the object size."""

    if not value:
        return None
    match = re.fullmatch(r"bytes=(\d*)-(\d*)", value.strip())
    if not match or (not match.group(1) and not match.group(2)) or size <= 0:
        raise ValueError("Range non valido")
    first, last = match.groups()
    if not first:
        count = int(last)
        if count <= 0:
            raise ValueError("Range non valido")
        return max(0, size - count), size - 1
    start = int(first)
    end = min(int(last), size - 1) if last else size - 1
    if start >= size or end < start:
        raise ValueError("Range non valido")
    return start, end


def _read_chunks(stream, length: int) -> Iterator[bytes]:
    """Yield bounded byte chunks from a stream without reading it all into memory."""

    remaining = length
    try:
        while remaining > 0:
            data = stream.read(min(1024 * 1024, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data
    finally:
        stream.close()


def build_pdf_response(storage: DocumentStorage, storage_key: str, byte_range: str | None):
    """Stream an authenticated original PDF with correct byte-range headers."""

    try:
        size = storage.get_size(storage_key)
    except FileNotFoundError:
        return Response(status_code=404, headers={"Cache-Control": "no-store"})
    headers = {
        "Accept-Ranges": "bytes",
        "Cache-Control": "private, no-store",
        "X-Content-Type-Options": "nosniff",
        "Content-Disposition": 'inline; filename="original.pdf"',
    }
    try:
        parsed = _parse_range(byte_range, size)
    except ValueError:
        return Response(status_code=416, headers={**headers, "Content-Range": f"bytes */{size}"})
    start, end = parsed if parsed else (0, size - 1)
    length = end - start + 1 if size else 0
    if parsed:
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
    headers["Content-Length"] = str(length)
    stream = storage.open_range(storage_key, start=start, end=end if parsed else None)
    return StreamingResponse(_read_chunks(stream, length), media_type="application/pdf", status_code=206 if parsed else 200, headers=headers)
