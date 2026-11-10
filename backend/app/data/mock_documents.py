from datetime import date

from app.schemas.analysis import (
    DocumentAnalysis,
    DocumentPage,
    EntityDefinition,
    EntitySegment,
    ExtractedField,
    ExtractedFieldStatus,
    TextOnlySegment,
)
from app.schemas.document import (
    DocumentCategory,
    DocumentDetailResponse,
    DocumentStatus,
    DocumentSummary,
)


READY_DOCUMENT = (
    DocumentDetailResponse(
        document=DocumentSummary(
            id=(
                "disciplinare-"
                "palermo-2027"
            ),
            name=(
                "Disciplinare_"
                "di_gara.pdf"
            ),
            category=(
                DocumentCategory
                .DISCIPLINARE
            ),
            pages=48,
            status=(
                DocumentStatus.READY
            ),
            uploaded_at=date(
                2026,
                11,
                9,
            ),
        ),
        analysis=DocumentAnalysis(
            entity_definitions=[
                EntityDefinition(
                    label=(
                        "ORGANIZZAZIONE"
                    ),
                    color="#dcecff",
                ),
                EntityDefinition(
                    label="IMPORTO",
                    color="#fff1b8",
                ),
                EntityDefinition(
                    label="DATA",
                    color="#e8ddf8",
                ),
                EntityDefinition(
                    label="ORA",
                    color="#f7d9ee",
                ),
                EntityDefinition(
                    label=(
                        "RIFERIMENTO_"
                        "NORMATIVO"
                    ),
                    color="#d9f0f0",
                ),
            ],
            pages=[
                DocumentPage(
                    page_number=12,
                    segments=[
                        TextOnlySegment(
                            type="text",
                            text=(
                                "La procedura "
                                "è indetta da "
                            ),
                        ),
                        EntitySegment(
                            type="entity",
                            id=(
                                "entity-"
                                "organization-1"
                            ),
                            text=(
                                "Comune di "
                                "Palermo"
                            ),
                            label=(
                                "ORGANIZZAZIONE"
                            ),
                        ),
                        TextOnlySegment(
                            type="text",
                            text=(
                                ".\n\nL'importo "
                                "complessivo "
                                "della procedura "
                                "è pari a "
                            ),
                        ),
                        EntitySegment(
                            type="entity",
                            id=(
                                "entity-"
                                "amount-1"
                            ),
                            text=(
                                "€ 1.250.000,00"
                            ),
                            label="IMPORTO",
                        ),
                        TextOnlySegment(
                            type="text",
                            text=(
                                ".\n\nIl termine "
                                "per la "
                                "presentazione "
                                "delle offerte è "
                            ),
                        ),
                        EntitySegment(
                            type="entity",
                            id=(
                                "entity-date-1"
                            ),
                            text=(
                                "31 marzo 2027"
                            ),
                            label="DATA",
                        ),
                        TextOnlySegment(
                            type="text",
                            text=" alle ore ",
                        ),
                        EntitySegment(
                            type="entity",
                            id=(
                                "entity-time-1"
                            ),
                            text="12:00",
                            label="ORA",
                        ),
                        TextOnlySegment(
                            type="text",
                            text=".",
                        ),
                    ],
                ),
                DocumentPage(
                    page_number=13,
                    segments=[
                        TextOnlySegment(
                            type="text",
                            text=(
                                "La procedura "
                                "è disciplinata "
                                "dal "
                            ),
                        ),
                        EntitySegment(
                            type="entity",
                            id=(
                                "entity-law-1"
                            ),
                            text=(
                                "D.Lgs. 36/2023"
                            ),
                            label=(
                                "RIFERIMENTO_"
                                "NORMATIVO"
                            ),
                        ),
                        TextOnlySegment(
                            type="text",
                            text=".",
                        ),
                    ],
                ),
            ],
            extracted_fields=[
                ExtractedField(
                    id=(
                        "field-contracting-"
                        "authority"
                    ),
                    label=(
                        "Stazione "
                        "appaltante"
                    ),
                    value=(
                        "Comune di Palermo"
                    ),
                    page=12,
                    confidence=0.96,
                    status=(
                        ExtractedFieldStatus
                        .EXTRACTED
                    ),
                ),
                ExtractedField(
                    id=(
                        "field-total-amount"
                    ),
                    label=(
                        "Importo "
                        "complessivo"
                    ),
                    value=(
                        "€ 1.250.000,00"
                    ),
                    page=12,
                    confidence=0.94,
                    status=(
                        ExtractedFieldStatus
                        .EXTRACTED
                    ),
                ),
                ExtractedField(
                    id="field-deadline",
                    label=(
                        "Scadenza offerte"
                    ),
                    value=(
                        "31/03/2027 "
                        "12:00"
                    ),
                    page=12,
                    confidence=0.91,
                    status=(
                        ExtractedFieldStatus
                        .EXTRACTED
                    ),
                ),
            ],
        ),
    )
)


PROCESSING_DOCUMENT = (
    DocumentDetailResponse(
        document=DocumentSummary(
            id=(
                "capitolato-"
                "servizi-cloud"
            ),
            name=(
                "Capitolato_"
                "servizi_cloud.pdf"
            ),
            category=(
                DocumentCategory
                .CAPITOLATO
            ),
            pages=72,
            status=(
                DocumentStatus
                .PROCESSING
            ),
            uploaded_at=date(
                2026,
                11,
                9,
            ),
        ),
        analysis=None,
    )
)


ERROR_DOCUMENT = (
    DocumentDetailResponse(
        document=DocumentSummary(
            id=(
                "contratto-"
                "servizio-demo"
            ),
            name=(
                "Contratto_"
                "servizio_demo.pdf"
            ),
            category=(
                DocumentCategory
                .CONTRATTO
            ),
            pages=31,
            status=(
                DocumentStatus.ERROR
            ),
            uploaded_at=date(
                2026,
                11,
                8,
            ),
        ),
        analysis=None,
    )
)


INITIAL_DOCUMENTS = [
    READY_DOCUMENT,
    PROCESSING_DOCUMENT,
    ERROR_DOCUMENT,
]