import os
from pathlib import Path
from typing import BinaryIO
from uuid import UUID

from app.core.exceptions import DocumentStorageError
from app.core.logging import get_logger


logger = get_logger("storage")


class DocumentStorage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()


    def save_original(
            self, 
            *, 
            owner_user_id: UUID, 
            document_id: UUID, 
            source: BinaryIO
            ) -> str:
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
        path = (self.root / storage_key).resolve()

        if path != self.root and self.root not in path.parents:
            logger.error("STORAGE | phase=invalid_storage_key | storage_key=%s", storage_key)

            raise DocumentStorageError("Storage key non valida.")

        return path


    def delete(self, storage_key: str) -> None:
        path = self.get_path(storage_key)

        try:
            path.unlink(missing_ok=True)
            logger.info("STORAGE | phase=delete_complete | storage_key=%s", storage_key)

        except Exception as exc:
            logger.exception("STORAGE | phase=delete_failed | storage_key=%s", storage_key)

            raise DocumentStorageError("Errore durante l'eliminazione del PDF.") from exc