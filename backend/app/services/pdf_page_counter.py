"""Conteggio delle pagine del PDF prima del caricamento nello storage.

Non richiede testo estraibile: gestisce anche PDF composti di sole immagini.
"""
from typing import BinaryIO
import pymupdf

from app.core.exceptions import InvalidDocumentFileError


def count_pdf_pages(source: BinaryIO) -> int:
    """Count pages in a seekable uploaded PDF stream without extracting text.

    The operation restores the original stream position so that subsequent
    storage writes can reuse the same input.
    """

    try:
        source.seek(0)
        pdf_bytes = source.read()
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if not pdf.is_pdf or pdf.page_count < 1:
                raise InvalidDocumentFileError("Il PDF non contiene pagine valide.")
            return pdf.page_count
    except (pymupdf.FileDataError, pymupdf.EmptyFileError, ValueError, RuntimeError) as exc:
        raise InvalidDocumentFileError("Il contenuto del PDF non è valido o è danneggiato.") from exc
    finally:
        source.seek(0)
