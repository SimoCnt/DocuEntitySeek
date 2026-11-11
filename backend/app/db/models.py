
from __future__ import annotations
from uuid import UUID
from typing import Any
from decimal import Decimal
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, Uuid, func, text as sql_text

from app.db.base import Base


# ============================================================
# PLANS
# ============================================================

class PlanModel(Base):
    __tablename__ = "plans"
    code: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    daily_analysis_limit: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    custom_schemas_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sql_text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    users: Mapped[list["UserModel"]] = relationship(back_populates="plan")


# ============================================================
# USERS
# ============================================================

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default=sql_text("'USER'"))
    plan_code: Mapped[str] = mapped_column(ForeignKey("plans.code", onupdate="CASCADE", ondelete="RESTRICT"), nullable=False, server_default=sql_text("'BASE'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    plan: Mapped["PlanModel"] = relationship(back_populates="users")
    documents: Mapped[list["DocumentModel"]] = relationship(back_populates="owner", passive_deletes=True)
    schemas: Mapped[list["ExtractionSchemaModel"]] = relationship(back_populates="owner", passive_deletes=True)


# ============================================================
# EXTRACTION SCHEMAS
# ============================================================

class ExtractionSchemaModel(Base):
    __tablename__ = "extraction_schemas"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    owner_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    domain: Mapped[str] = mapped_column(String(120), nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sql_text("FALSE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    owner: Mapped["UserModel | None"] = relationship(back_populates="schemas")
    versions: Mapped[list["ExtractionSchemaVersionModel"]] = relationship(back_populates="schema", passive_deletes=True)


class ExtractionSchemaVersionModel(Base):
    __tablename__ = "extraction_schema_versions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    schema_id: Mapped[UUID] = mapped_column(ForeignKey("extraction_schemas.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sql_text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    schema: Mapped["ExtractionSchemaModel"] = relationship(back_populates="versions")
    entity_definitions: Mapped[list["EntityDefinitionModel"]] = relationship(back_populates="schema_version", passive_deletes=True)
    field_definitions: Mapped[list["FieldDefinitionModel"]] = relationship(back_populates="schema_version", passive_deletes=True)
    analyses: Mapped[list["AnalysisModel"]] = relationship(back_populates="schema_version")


class EntityDefinitionModel(Base):
    __tablename__ = "entity_definitions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    schema_version_id: Mapped[UUID] = mapped_column(ForeignKey("extraction_schema_versions.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=sql_text("0"))
    schema_version: Mapped["ExtractionSchemaVersionModel"] = relationship(back_populates="entity_definitions")


class FieldDefinitionModel(Base):
    __tablename__ = "field_definitions"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    schema_version_id: Mapped[UUID] = mapped_column(ForeignKey("extraction_schema_versions.id", ondelete="CASCADE"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    data_type: Mapped[str] = mapped_column(String(30), nullable=False, server_default=sql_text("'string'"))
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sql_text("FALSE"))
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=sql_text("0"))
    schema_version: Mapped["ExtractionSchemaVersionModel"] = relationship(back_populates="field_definitions")


# ============================================================
# DOCUMENTS
# ============================================================

class DocumentModel(Base):
    __tablename__ = "documents"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    owner_user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=sql_text("'PROCESSING'"))
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    owner: Mapped["UserModel"] = relationship(back_populates="documents")
    pages: Mapped[list["DocumentPageModel"]] = relationship(back_populates="document", passive_deletes=True, order_by="DocumentPageModel.page_number")
    analyses: Mapped[list["AnalysisModel"]] = relationship(back_populates="document", passive_deletes=True)


class DocumentPageModel(Base):
    __tablename__ = "document_pages"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    global_start: Mapped[int] = mapped_column(Integer, nullable=False)
    global_end: Mapped[int] = mapped_column(Integer, nullable=False)
    document: Mapped["DocumentModel"] = relationship(back_populates="pages")


# ============================================================
# ANALYSES
# ============================================================

class AnalysisModel(Base):
    __tablename__ = "analyses"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    schema_version_id: Mapped[UUID] = mapped_column(ForeignKey("extraction_schema_versions.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default=sql_text("'PENDING'"))
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default=sql_text("'{}'::jsonb"))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    document: Mapped["DocumentModel"] = relationship(back_populates="analyses")
    schema_version: Mapped["ExtractionSchemaVersionModel"] = relationship(back_populates="analyses")
    entity_occurrences: Mapped[list["EntityOccurrenceModel"]] = relationship(back_populates="analysis", passive_deletes=True)
    extracted_fields: Mapped[list["ExtractedFieldModel"]] = relationship(back_populates="analysis", passive_deletes=True)


class EntityOccurrenceModel(Base):
    __tablename__ = "entity_occurrences"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    analysis_id: Mapped[UUID] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    global_start: Mapped[int] = mapped_column(Integer, nullable=False)
    global_end: Mapped[int] = mapped_column(Integer, nullable=False)
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    page_start: Mapped[int] = mapped_column(Integer, nullable=False)
    page_end: Mapped[int] = mapped_column(Integer, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=sql_text("TRUE"))
    analysis: Mapped["AnalysisModel"] = relationship(back_populates="entity_occurrences")


class ExtractedFieldModel(Base):
    __tablename__ = "extracted_fields"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    analysis_id: Mapped[UUID] = mapped_column(ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    global_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    global_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    analysis: Mapped["AnalysisModel"] = relationship(back_populates="extracted_fields")
    candidates: Mapped[list["FieldCandidateModel"]] = relationship(back_populates="extracted_field", passive_deletes=True)


class FieldCandidateModel(Base):
    __tablename__ = "field_candidates"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, server_default=sql_text("gen_random_uuid()"))
    extracted_field_id: Mapped[UUID] = mapped_column(ForeignKey("extracted_fields.id", ondelete="CASCADE"), nullable=False)
    value_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    global_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    global_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    candidate_rank: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    extracted_field: Mapped["ExtractedFieldModel"] = relationship(back_populates="candidates")
