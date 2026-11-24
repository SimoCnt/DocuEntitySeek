"""Validate PDF uploads against content-type, file-signature, and size constraints."""

from fastapi import UploadFile

from app.core.exceptions import InvalidDocumentFileError
from app.core.logging import get_logger
from app.core.config import get_settings


logger = get_logger("validation")


def validate_pdf_upload(file: UploadFile) -> None:
    """Reject oversized, mislabeled, or invalid PDF uploads before persistence."""

    logger.info(
        "PDF_VALIDATION | "
        "phase=start | "
        "filename=%r | "
        "content_type=%s | "
        "size_bytes=%s",
        file.filename,
        file.content_type,
        file.size,
    )

    if not file.filename:
        logger.warning(
            "PDF_VALIDATION | "
            "phase=rejected | "
            "reason=invalid_extension | "
            "filename=%r",
            file.filename,
        )

        raise InvalidDocumentFileError("Il file deve avere un nome.")

    if not file.filename.lower().endswith(".pdf"):
        logger.warning(
            "PDF_VALIDATION | "
            "phase=rejected | "
            "reason=invalid_extension | "
            "filename=%r",
            file.filename,
        )

        raise InvalidDocumentFileError("Il file deve avere estensione .pdf.")

    settings = get_settings()

    if file.size is not None and file.size > settings.max_pdf_size_bytes:
        max_size_mb = settings.max_pdf_size_bytes // (1024 * 1024)

        raise InvalidDocumentFileError(f"Il PDF supera il limite massimo di {max_size_mb} MB")

    header = file.file.read(1024)
    file.file.seek(0)

    logger.info(
        "PDF_VALIDATION | "
        "phase=complete | "
        "filename=%r",
        file.filename,
    )

    if b"%PDF-" not in header:
        raise InvalidDocumentFileError("Il contenuto del file non sembra essere un PDF valido.")
