"""SQLAlchemy document repository."""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from l1_support_bot.domain.errors import DuplicateDocumentError
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.ingestion import IngestionStatus
from l1_support_bot.infrastructure.persistence.models.documents import DocumentModel


def _to_domain(model: DocumentModel) -> Document:
    return Document(
        id=UUID(model.id),
        name=model.name,
        original_filename=model.original_filename,
        file_type=FileType(model.file_type),
        source_type=SourceType(model.source_type),
        checksum=model.checksum,
        storage_path=model.storage_path,
        file_size_bytes=model.file_size_bytes,
        status=IngestionStatus(model.status),
        uploaded_at=model.uploaded_at,
        updated_at=model.updated_at,
        description=model.description,
    )


class SqlAlchemyDocumentRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def get(self, document_id: UUID) -> Document | None:
        async with self.session_factory() as session:
            model = await session.get(DocumentModel, str(document_id))
            return _to_domain(model) if model else None

    async def get_by_checksum(self, checksum: str) -> Document | None:
        async with self.session_factory() as session:
            model = await session.scalar(
                select(DocumentModel).where(DocumentModel.checksum == checksum)
            )
            return _to_domain(model) if model else None

    async def save(self, document: Document) -> Document:
        model = DocumentModel(
            id=str(document.id),
            name=document.name,
            original_filename=document.original_filename,
            file_type=document.file_type.value,
            source_type=document.source_type.value,
            storage_path=document.storage_path,
            checksum=document.checksum,
            file_size_bytes=document.file_size_bytes,
            status=document.status.value,
            uploaded_at=document.uploaded_at,
            updated_at=document.updated_at,
            description=document.description,
        )
        async with self.session_factory() as session:
            try:
                await session.merge(model)
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                raise DuplicateDocumentError(
                    "A document with identical content is already registered."
                ) from exc
        return document

    async def list(
        self,
        *,
        status: IngestionStatus | None = None,
        source_type: SourceType | None = None,
    ) -> Sequence[Document]:
        async with self.session_factory() as session:
            statement = select(DocumentModel).order_by(DocumentModel.uploaded_at.desc())
            if status is not None:
                statement = statement.where(DocumentModel.status == status.value)
            if source_type is not None:
                statement = statement.where(DocumentModel.source_type == source_type.value)
            result = await session.scalars(statement)
            return tuple(_to_domain(model) for model in result)

    async def update_status(self, document_id: UUID, status: IngestionStatus) -> Document:
        document = await self.get(document_id)
        if document is None:
            raise LookupError(f"Document {document_id} was not found")
        return await self.save(document.transition_to(status))

    async def delete(self, document_id: UUID) -> None:
        async with self.session_factory() as session:
            model = await session.get(DocumentModel, str(document_id))
            if model is not None:
                await session.delete(model)
                await session.commit()