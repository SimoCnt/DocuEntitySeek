"""Query schema visibility and custom-schema capabilities for a specific user."""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import ExtractionSchemaModel, ExtractionSchemaVersionModel, PlanModel, UserModel


class SchemaAccessRepository:
    """Read plan-dependent visibility of built-in and custom schema versions."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_custom_schemas_enabled(self, user_id: UUID) -> bool | None:
        """Check whether the account's subscription permits custom schemas."""

        statement = (
            select(PlanModel.custom_schemas_enabled)
            .join(UserModel, UserModel.plan_code == PlanModel.code)
            .where(UserModel.id == user_id)
        )

        return self.session.scalar(statement)

    def list_available_versions(
        self,
        *,
        user_id: UUID,
        include_custom: bool,
    ) -> list[tuple[ExtractionSchemaModel, ExtractionSchemaVersionModel]]:
        """Find schema versions visible to a user under the current plan."""

        access_condition = ExtractionSchemaModel.is_builtin.is_(True)

        if include_custom:
            access_condition = or_(
                ExtractionSchemaModel.is_builtin.is_(True),
                ExtractionSchemaModel.owner_user_id == user_id,
            )

        statement = (
            select(ExtractionSchemaModel, ExtractionSchemaVersionModel)
            .join(ExtractionSchemaVersionModel, ExtractionSchemaVersionModel.schema_id == ExtractionSchemaModel.id)
            .where(
                ExtractionSchemaModel.archived_at.is_(None),
                ExtractionSchemaVersionModel.is_active.is_(True),
                access_condition,
            )
            .order_by(ExtractionSchemaModel.is_builtin.desc(), ExtractionSchemaModel.name.asc())
        )

        return list(self.session.execute(statement).tuples().all())

    def get_visible_version(
        self,
        *,
        user_id: UUID,
        schema_version_id: UUID,
    ) -> tuple[ExtractionSchemaModel, ExtractionSchemaVersionModel] | None:
        """Resolve a particular schema version only if visible to the user."""

        statement = (
            select(ExtractionSchemaModel, ExtractionSchemaVersionModel)
            .join(ExtractionSchemaVersionModel, ExtractionSchemaVersionModel.schema_id == ExtractionSchemaModel.id)
            .where(
                ExtractionSchemaVersionModel.id == schema_version_id,
                ExtractionSchemaVersionModel.is_active.is_(True),
                ExtractionSchemaModel.archived_at.is_(None),
                or_(
                    ExtractionSchemaModel.is_builtin.is_(True),
                    ExtractionSchemaModel.owner_user_id == user_id,
                ),
            )
        )

        return self.session.execute(statement).tuples().one_or_none()
