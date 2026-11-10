class DocumentNotFoundError(Exception):
    def __init__(self, document_id: str):
        self.document_id = (document_id)
        super().__init__(f"Documento '{document_id}' non trovato.")


class InvalidDocumentFileError(Exception):
    pass