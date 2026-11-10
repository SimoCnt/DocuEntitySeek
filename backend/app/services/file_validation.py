from fastapi import UploadFile

from app.core.exceptions import InvalidDocumentFileError


async def validate_pdf_upload(file: UploadFile) -> None:
    if not file.filename: 
        raise (InvalidDocumentFileError("Il file deve avere un nome."))

    if not file.filename.lower().endswith(".pdf"):
        raise InvalidDocumentFileError("Il file deve avere estensione .pdf.")        

    header = await file.read(1024)
    await file.seek(0)

    if b"%PDF-" not in header:
        raise InvalidDocumentFileError("Il contenuto del file non sembra essere un PDF valido.")
        