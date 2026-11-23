
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from functools import lru_cache

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ForbiddenError
from app.core.security import decode_access_token, oauth2_scheme
from app.db.session import get_db_session
from app.db.models import UserModel
from app.repositories.user_repository import UserRepository
from app.services.document_service import DocumentService
from app.services.document_storage import DocumentStorage, S3DocumentStorage
from app.services.auth_service import AuthService
from app.pipeline.pdf_text_extractor import PdfTextExtractor
from app.pipeline.provenance import DocumentProvenanceBuilder
from app.services.document_preparation_service import DocumentPreparationService
from app.pipeline.config_resolver import AiConfigurationResolver
from app.pipeline.model_provider import AiModelProvider, Gliner2ModelLoader
from app.pipeline.ner_extractor import Gliner2NerExtractor
from app.pipeline.field_extractor import Gliner2FieldExtractor
from app.pipeline.candidate_deduplicator import CandidateDeduplicator
from app.pipeline.viewer_overlap_resolver import ViewerOverlapResolver
from app.pipeline.page_span_mapper import PageSpanMapper
from app.services.entity_occurrence_persistence_service import EntityOccurrencePersistenceService
from app.pipeline.field_result_resolver import FieldResultResolver
from app.services.field_result_persistence_service import FieldResultPersistenceService
from app.pipeline.analysis_pipeline import AnalysisPipeline
from app.services.analysis_services import AnalysisService
from app.repositories.analysis_quota_repository import AnalysisQuotaRepository
from app.services.analysis_quota_service import AnalysisQuotaService
from app.services.analysis_query_service import AnalysisQueryService
from app.repositories.schema_access_repository import SchemaAccessRepository
from app.services.schema_access_service import SchemaAccessService
from app.services.custom_schema_service import CustomSchemaService


DbSessionDep = Annotated[Session, Depends(get_db_session)]


@lru_cache(maxsize=1)
def get_document_storage() -> DocumentStorage:
    settings = get_settings()
    
    backend = settings.document_storage_backend.lower()
    if backend == "local":
        return DocumentStorage(settings.document_storage_root)
    if backend == "s3":
        import boto3
        from botocore.config import Config
        if not settings.document_s3_bucket:
            raise ValueError("DOCUMENT_S3_BUCKET deve essere configurato.")
        if bool(settings.document_s3_access_key) != bool(settings.document_s3_secret_key):
            raise ValueError("Configurare entrambe le credenziali S3 o utilizzare credenziali IAM.")
        client = boto3.client(
            "s3", endpoint_url=settings.document_s3_endpoint_url,
            region_name=settings.document_s3_region,
            aws_access_key_id=settings.document_s3_access_key,
            aws_secret_access_key=settings.document_s3_secret_key,
            config=Config(s3={"addressing_style": "path"}, signature_version="s3v4"),
        )
        return S3DocumentStorage(settings.document_storage_root, bucket=settings.document_s3_bucket, client=client)
    raise ValueError(f"DOCUMENT_STORAGE_BACKEND non supportato: {backend}")


DocumentStorageDep = Annotated[DocumentStorage, Depends(get_document_storage)]


def get_document_service(session: DbSessionDep, storage: DocumentStorageDep) -> DocumentService:
    return DocumentService(session, storage)


def get_auth_service(session: DbSessionDep) -> AuthService:
    return AuthService(session)


def get_current_user(session: DbSessionDep, token: Annotated[str | None, Depends(oauth2_scheme)]) -> UserModel:
    if token is None:
        raise AuthenticationError("Autenticazione richiesta.")

    user_id = decode_access_token(token)
    user = UserRepository(session).get_by_id(user_id)

    if user is None:
        raise AuthenticationError("Utente associato al token non trovato.")

    if not user.is_active:
        raise ForbiddenError("Account disabilitato.")

    return user


CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


def require_admin(current_user: CurrentUserDep) -> UserModel:
    if current_user.role != "ADMIN":
        raise ForbiddenError("Permessi amministrativi richiesti.")

    return current_user


DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AdminUserDep = Annotated[UserModel, Depends(require_admin)]


def get_pdf_text_extractor() -> PdfTextExtractor:
    settings = get_settings()

    return PdfTextExtractor(sort_text=settings.pdf_text_sort)


PdfTextExtractorDep = Annotated[PdfTextExtractor, Depends(get_pdf_text_extractor)]


def get_provenance_builder() -> DocumentProvenanceBuilder:
    return (DocumentProvenanceBuilder())


ProvenanceBuilderDep = Annotated[DocumentProvenanceBuilder, Depends(get_provenance_builder)]


def get_document_preparation_service(
    session: DbSessionDep,
    storage: DocumentStorageDep,
    pdf_extractor: PdfTextExtractorDep,
    provenance_builder: ProvenanceBuilderDep,
) -> DocumentPreparationService:
    return (DocumentPreparationService(
        session=session,
        storage=storage,
        pdf_extractor=(pdf_extractor),
        provenance_builder=(provenance_builder)
        )
    )


DocumentPreparationServiceDep = Annotated[DocumentPreparationService, Depends(get_document_preparation_service)]


def get_ai_configuration_resolver(session: DbSessionDep) -> AiConfigurationResolver:
    return AiConfigurationResolver(session)


AiConfigurationResolverDep = Annotated[AiConfigurationResolver, Depends(get_ai_configuration_resolver)]


@lru_cache(maxsize=1)
def get_ai_model_provider() -> AiModelProvider:
    settings = get_settings()

    return AiModelProvider(
        loaders={"GLINER2": (Gliner2ModelLoader())},
        requested_device=(settings.ai_model_device),
        quantize=(settings.ai_model_quantize),
        compile_model=(settings.ai_model_compile)
    )


AiModelProviderDep = Annotated[AiModelProvider, Depends(get_ai_model_provider)]


def get_gliner2_ner_extractor() -> Gliner2NerExtractor:
    return Gliner2NerExtractor()


Gliner2NerExtractorDep = Annotated[Gliner2NerExtractor, Depends(get_gliner2_ner_extractor)]


def get_gliner2_field_extractor() -> Gliner2FieldExtractor:
    return Gliner2FieldExtractor()


Gliner2FieldExtractorDep = Annotated[Gliner2FieldExtractor, Depends(get_gliner2_field_extractor)]


def get_candidate_deduplicator() -> CandidateDeduplicator:
    return CandidateDeduplicator()


CandidateDeduplicatorDep = Annotated[CandidateDeduplicator, Depends(get_candidate_deduplicator)]


def get_viewer_overlap_resolver() -> ViewerOverlapResolver:
    return ViewerOverlapResolver()


ViewerOverlapResolverDep = Annotated[ViewerOverlapResolver, Depends(get_viewer_overlap_resolver)]


def get_page_span_mapper() -> PageSpanMapper:
    return PageSpanMapper()


PageSpanMapperDep = Annotated[PageSpanMapper, Depends(get_page_span_mapper)]


def get_entity_occurrence_persistence_service(session: DbSessionDep) -> EntityOccurrencePersistenceService:
    return EntityOccurrencePersistenceService(session)


EntityOccurrencePersistenceServiceDep = Annotated[EntityOccurrencePersistenceService, Depends(get_entity_occurrence_persistence_service)]


def get_field_result_resolver() -> FieldResultResolver:
    return FieldResultResolver()


FieldResultResolverDep = Annotated[FieldResultResolver, Depends(get_field_result_resolver)]


def get_field_result_persistence_service(session: DbSessionDep) -> FieldResultPersistenceService:
    return FieldResultPersistenceService(session)


FieldResultPersistenceServiceDep = Annotated[FieldResultPersistenceService, Depends(get_field_result_persistence_service)]


def get_analysis_pipeline(
    preparation_service: DocumentPreparationServiceDep,
    model_provider: AiModelProviderDep,
    ner_extractor: Gliner2NerExtractorDep,
    field_extractor: Gliner2FieldExtractorDep,
    deduplicator: CandidateDeduplicatorDep,
    overlap_resolver: ViewerOverlapResolverDep,
    page_mapper: PageSpanMapperDep,
    field_resolver: FieldResultResolverDep,
    entity_persistence: EntityOccurrencePersistenceServiceDep,
    field_persistence: FieldResultPersistenceServiceDep,
) -> AnalysisPipeline:
    return AnalysisPipeline(
        preparation_service=preparation_service,
        model_provider=model_provider,
        ner_extractor=ner_extractor,
        field_extractor=field_extractor,
        deduplicator=deduplicator,
        overlap_resolver=overlap_resolver,
        page_mapper=page_mapper,
        field_resolver=field_resolver,
        entity_persistence=entity_persistence,
        field_persistence=field_persistence,
    )


AnalysisPipelineDep = Annotated[AnalysisPipeline, Depends(get_analysis_pipeline)]


def get_analysis_quota_service(session: DbSessionDep) -> AnalysisQuotaService:
    return AnalysisQuotaService(AnalysisQuotaRepository(session))


AnalysisQuotaServiceDep = Annotated[AnalysisQuotaService, Depends(get_analysis_quota_service)]



def get_schema_access_service(session: DbSessionDep) -> SchemaAccessService:
    return SchemaAccessService(SchemaAccessRepository(session))


SchemaAccessServiceDep = Annotated[SchemaAccessService, Depends(get_schema_access_service)]


def get_custom_schema_service(session: DbSessionDep, schema_access_service: SchemaAccessServiceDep) -> CustomSchemaService:
    return CustomSchemaService(session=session, schema_access_service=schema_access_service)


CustomSchemaServiceDep = Annotated[CustomSchemaService, Depends(get_custom_schema_service)]


def get_analysis_service(
    session: DbSessionDep,
    config_resolver: AiConfigurationResolverDep,
    quota_service: AnalysisQuotaServiceDep,
    schema_access_service: SchemaAccessServiceDep,
    pipeline: AnalysisPipelineDep,
) -> AnalysisService:
    return AnalysisService(
        session=session,
        config_resolver=config_resolver,
        quota_service=quota_service,
        schema_access_service=schema_access_service,
        pipeline=pipeline,
    )


AnalysisServiceDep = Annotated[AnalysisService, Depends(get_analysis_service)]


def get_analysis_query_service(session: DbSessionDep) -> AnalysisQueryService:
    return AnalysisQueryService(session)


AnalysisQueryServiceDep = Annotated[AnalysisQueryService, Depends(get_analysis_query_service)]
