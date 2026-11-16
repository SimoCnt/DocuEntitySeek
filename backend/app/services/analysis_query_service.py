from collections import defaultdict
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.analysis import AnalysisStatus
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.document_page_repository import DocumentPageRepository
from app.repositories.entity_occurrence_repository import EntityOccurrenceRepository
from app.repositories.extracted_field_repository import ExtractedFieldRepository
from app.repositories.field_candidate_repository import FieldCandidateRepository


class AnalysisQueryService:
    def __init__(self, session: Session) -> None:
        self.analyses = AnalysisRepository(session)
        self.pages = DocumentPageRepository(session)
        self.entities = EntityOccurrenceRepository(session)
        self.fields = ExtractedFieldRepository(session)
        self.candidates = FieldCandidateRepository(session)


    def list_for_document(self, *, document_id: UUID, owner_user_id: UUID):
        return self.analyses.list_for_document_and_owner(document_id=document_id, owner_user_id=owner_user_id)


    def get_detail(self, *, analysis_id: UUID, document_id: UUID, owner_user_id: UUID):
        analysis = self.analyses.get_for_document_and_owner(
            analysis_id=analysis_id,
            document_id=document_id,
            owner_user_id=owner_user_id,
        )

        if analysis is None:
            raise LookupError("Analysis non trovata.")

        if analysis.status != AnalysisStatus.READY.value:
            return analysis, [], [], [], {}

        pages = self.pages.list_for_document(document_id)
        entities = self.entities.list_for_analysis(analysis_id)
        fields = self.fields.list_for_analysis(analysis_id)
        candidates = self.candidates.list_for_extracted_fields([field.id for field in fields])

        candidates_by_field = defaultdict(list)

        for candidate in candidates:
            candidates_by_field[candidate.extracted_field_id].append(candidate)

        return analysis, pages, entities, fields, candidates_by_field