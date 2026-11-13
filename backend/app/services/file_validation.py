
from fastapi import UploadFile

from app.core.exceptions import InvalidDocumentFileError
from app.core.logging import get_logger


logger = get_logger("validation")


def validate_pdf_upload(file: UploadFile) -> None:
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
