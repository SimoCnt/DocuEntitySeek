"""Provide local and S3-compatible private PDF storage with materialization and range reads."""

import os
from pathlib import Path
from contextlib import contextmanager
from tempfile import TemporaryDirectory
import shutil
from typing import BinaryIO
from uuid import UUID

from app.core.exceptions import DocumentStorageError
from app.core.logging import get_logger


logger = get_logger("storage")


class DocumentStorage:
    """Store private original PDFs on the local filesystem using safe relative keys."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()


    def save_original(
            self, 
            *, 
            owner_user_id: UUID, 
            document_id: UUID, 
            source: BinaryIO
            ) -> str:
        """Write the original PDF to a private local path using an atomic rename.

        The upload is staged in a temporary file, synchronized to disk, and
        moved into place; the source stream is reset for callers.
        """

        relative_path = Path(str(owner_user_id)) / str(document_id) / "original.pdf"
        destination = self.root / relative_path
        temporary = destination.parent / "original.pdf.part"

        logger.info(
            "STORAGE | phase=save_start | document_id=%s | owner_user_id=%s | storage_key=%s",
            document_id,
            owner_user_id,
            relative_path.as_posix(),
        )

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.seek(0)
            written_bytes = 0

            with temporary.open("wb") as output:
                while True:
                    chunk = source.read(1024 * 1024)

                    if not chunk:
                        break

                    output.write(chunk)
                    written_bytes += len(chunk)

                output.flush()
                os.fsync(output.fileno())

            os.replace(temporary, destination)
            source.seek(0)

            logger.info(
                "STORAGE | phase=save_complete | document_id=%s | bytes=%d | storage_key=%s",
                document_id,
                written_bytes,
                relative_path.as_posix(),
            )

            return relative_path.as_posix()

        except Exception as exc:
            temporary.unlink(missing_ok=True)
            logger.exception("STORAGE | phase=save_failed | document_id=%s", document_id)

            raise DocumentStorageError("Errore durante la persistenza del PDF.") from exc


    def get_path(self, storage_key: str) -> Path:
        """Resolve a storage key beneath the configured root, rejecting path traversal."""

        path = (self.root / storage_key).resolve()

        if path != self.root and self.root not in path.parents:
            logger.error("STORAGE | phase=invalid_storage_key | storage_key=%s", storage_key)

            raise DocumentStorageError("Storage key non valida.")

        return path


    def delete(self, storage_key: str) -> None:
        """Delete a local original PDF, tolerating an already missing file."""

        path = self.get_path(storage_key)

        try:
            path.unlink(missing_ok=True)
            logger.info("STORAGE | phase=delete_complete | storage_key=%s", storage_key)

        except Exception as exc:
            logger.exception("STORAGE | phase=delete_failed | storage_key=%s", storage_key)

            raise DocumentStorageError("Errore durante l'eliminazione del PDF.") from exc

    def get_size(self, storage_key: str) -> int:
        """Return the size of a stored local PDF, raising if it does not exist."""

        path = self.get_path(storage_key)
        if not path.is_file():
            raise FileNotFoundError("PDF originale non trovato.")
        return path.stat().st_size


    def open_range(self, storage_key: str, start: int = 0, end: int | None = None):
        """Open a bounded binary read stream from a stored original PDF."""

        path = self.get_path(storage_key)
        if not path.is_file():
            raise FileNotFoundError("PDF originale non trovato.")
        stream = path.open("rb")
        stream.seek(start)
        return stream


    @contextmanager
    def materialize(self, storage_key: str):
        """Expose a local PDF path within a context manager for parser access."""

        path = self.get_path(storage_key)
        if not path.is_file():
            raise DocumentStorageError("Il PDF originale non esiste nello storage.")
        yield path


class S3DocumentStorage(DocumentStorage):
    """Scrive sempre in S3; i file precedenti sono leggibili dal filesystem locale.

    L'object storage non e' pubblico: solo l'API applicativa puo' accedervi.
    Questa compatibilita' di lettura e' temporanea, fino alla migrazione del punto 5.
    """
    def __init__(self, root: Path, *, bucket: str, client) -> None:
        super().__init__(root)
        if not bucket:
            raise ValueError("Il bucket S3 non puo' essere vuoto.")
        self.bucket = bucket
        self.client = client


    @staticmethod
    def _is_not_found(error: Exception) -> bool:
        """Identify an object-not-found response without treating all storage failures as missing.
        """

        response = getattr(error, "response", None)
        code = (response or {}).get("Error", {}).get("Code", "")
        return str(code) in {"404", "NoSuchKey", "NotFound"}


    @staticmethod
    def _key(owner_user_id: UUID, document_id: UUID) -> str:
        """Construct a deterministic owner-scoped S3 key for an original PDF."""

        return f"{owner_user_id}/{document_id}/original.pdf"

    
    def save_original(self, *, owner_user_id: UUID, document_id: UUID, source: BinaryIO) -> str:
        """Upload the original PDF to a private S3-compatible bucket and return its key."""

        key = self._key(owner_user_id, document_id)
        try:
            source.seek(0)
            self.client.upload_fileobj(source, self.bucket, key, ExtraArgs={"ContentType": "application/pdf"})
            logger.info("STORAGE | s3_upload_complete | document_id=%s | storage_key=%s", document_id, key)
            return key
        except Exception as exc:
            logger.exception("STORAGE | s3_upload_failed | document_id=%s", document_id)
            raise DocumentStorageError("Impossibile salvare il PDF nello storage S3.") from exc


    def get_size(self, storage_key: str) -> int:
        """Query remote object size, with compatibility fallback for legacy local PDFs."""

        self.get_path(storage_key)  # valida chiave anche per S3
        try:
            response = self.client.head_object(Bucket=self.bucket, Key=storage_key)
            return int(response["ContentLength"])
        except Exception as exc:
            if self._is_not_found(exc):
                return super().get_size(storage_key)  # solo documenti legacy
            logger.exception("STORAGE | s3_head_failed | storage_key=%s", storage_key)
            raise DocumentStorageError("Impossibile leggere i metadati del PDF.") from exc


    def open_range(self, storage_key: str, start: int = 0, end: int | None = None):
        """Stream a requested remote byte range, falling back to legacy local storage."""

        self.get_path(storage_key)  # valida chiave anche per S3
        args = {"Bucket": self.bucket, "Key": storage_key}
        if start > 0 or end is not None:
            args["Range"] = f"bytes={start}-{'' if end is None else end}"
        try:
            response = self.client.get_object(**args)
            return response["Body"]
        except Exception as exc:
            if self._is_not_found(exc):
                return super().open_range(storage_key, start=start, end=end)
            logger.exception("STORAGE | s3_download_failed | storage_key=%s", storage_key)
            raise DocumentStorageError("Impossibile leggere il PDF dallo storage S3.") from exc


    @contextmanager
    def materialize(self, storage_key: str):
        """Download an S3 object into a temporary local path for PDF processing."""

        with TemporaryDirectory(prefix="docuentityseek-pdf-") as directory:
            destination = Path(directory) / "original.pdf"
            stream = self.open_range(storage_key)
            try:
                with destination.open("wb") as output:
                    shutil.copyfileobj(stream, output, length=1024 * 1024)
            except Exception as exc:
                raise DocumentStorageError("Impossibile preparare il PDF per l'analisi.") from exc
            finally:
                stream.close()
            yield destination  # cancellato anche in caso di errore del motore AI


    def delete(self, storage_key: str) -> None:
        """Delete the remote original object, with legacy storage cleanup as applicable."""

        self.get_path(storage_key)  # valida chiave
        try:
            self.client.delete_object(Bucket=self.bucket, Key=storage_key)
        except Exception as exc:
            logger.exception("STORAGE | s3_delete_failed | storage_key=%s", storage_key)
            raise DocumentStorageError("Impossibile eliminare il PDF da S3.") from exc

