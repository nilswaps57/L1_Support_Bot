from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.models.configuration import (
    ChunkingConfig,
    EmbeddingConfig,
    LLMConfig,
    RetrievalConfig,
)
from l1_support_bot.domain.models.document import Document, FileType, SourceType
from l1_support_bot.domain.models.feedback import Feedback, FeedbackRating
from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus
from l1_support_bot.domain.models.session import ChatMessage, ChatSession, MessageRole


def test_document_has_safe_identity_and_initial_status() -> None:
    document = Document.new(
        name="FLEXCUBE Manual.pdf",
        original_filename="../../FLEXCUBE Manual.pdf",
        file_type=FileType.PDF,
        source_type=SourceType.FLEXCUBE_MANUAL,
        checksum="a" * 64,
        storage_path="documents/123.pdf",
        file_size_bytes=100,
    )

    assert isinstance(document.id, UUID)
    assert document.status is IngestionStatus.UPLOADED
    assert document.checksum == "a" * 64


def test_document_rejects_invalid_checksum_and_size() -> None:
    with pytest.raises(ValueError):
        Document.new(
            name="manual.pdf",
            original_filename="manual.pdf",
            file_type=FileType.PDF,
            source_type=SourceType.OTHER,
            checksum="bad",
            storage_path="documents/file.pdf",
            file_size_bytes=1,
        )

    with pytest.raises(ValueError):
        Document.new(
            name="manual.pdf",
            original_filename="manual.pdf",
            file_type=FileType.PDF,
            source_type=SourceType.OTHER,
            checksum="a" * 64,
            storage_path="documents/file.pdf",
            file_size_bytes=0,
        )


def test_ingestion_job_tracks_warning_and_counts() -> None:
    job = IngestionJob.new(uuid4())
    job = job.transition_to(IngestionStatus.PARSING)
    job = job.transition_to(IngestionStatus.NORMALISING)
    job = job.transition_to(IngestionStatus.CHUNKING)
    job = job.transition_to(IngestionStatus.READY_FOR_INDEXING_WITH_WARNING)
    job = job.transition_to(IngestionStatus.EMBEDDING)
    job = job.transition_to(IngestionStatus.INDEXING)
    warning_job = job.with_progress(
        status=IngestionStatus.COMPLETED_WITH_WARNING,
        chunks_created=3,
        chunks_indexed=2,
        parse_warnings=("A table was omitted",),
    )

    assert warning_job.is_terminal
    assert warning_job.has_warnings
    assert warning_job.chunks_indexed == 2


def test_citation_identity_is_chunk_based() -> None:
    chunk_id = uuid4()
    citation = Citation(
        chunk_id=chunk_id,
        document_id=uuid4(),
        document_name="Manual",
        page_number=4,
        section="Task Codes",
        task_code="BA435",
    )

    assert citation.identity == chunk_id
    assert citation.task_code == "BA435"


def test_answer_types_and_citation_rules() -> None:
    insufficient = Answer.insufficient("No supporting evidence.")
    grounded = Answer(
        question="What is BA435?",
        answer_text="The source describes BA435.",
        answer_type=AnswerType.GROUNDED,
        citations=(
            Citation(
                chunk_id=uuid4(), document_id=uuid4(), document_name="Manual"
            ),
        ),
    )

    assert insufficient.answer_type is AnswerType.INSUFFICIENT
    assert insufficient.insufficient_information
    assert grounded.citations
    with pytest.raises(ValueError):
        Answer(
            question="Question",
            answer_text="Answer",
            answer_type=AnswerType.GROUNDED,
            citations=(),
        )


def test_session_expiry_and_message_order() -> None:
    now = datetime.now(UTC)
    session = ChatSession.new(ttl=timedelta(minutes=10), now=now)
    message = ChatMessage(
        session_id=session.id,
        role=MessageRole.USER,
        content="What is BA435?",
        turn_order=0,
    )

    assert session.expires_at == now + timedelta(minutes=10)
    assert not session.is_expired(now + timedelta(minutes=9))
    assert session.is_expired(now + timedelta(minutes=11))
    assert message.turn_order == 0


def test_feedback_validates_rating_and_comment_length() -> None:
    feedback = Feedback.new(
        answer_id=uuid4(),
        session_id=uuid4(),
        question="Question",
        answer_text="Answer",
        rating=FeedbackRating.HELPFUL,
        comment="Clear",
    )

    assert feedback.rating is FeedbackRating.HELPFUL
    with pytest.raises(ValueError):
        Feedback.new(
            answer_id=uuid4(),
            session_id=uuid4(),
            question="Question",
            answer_text="Answer",
            rating=FeedbackRating.NOT_HELPFUL,
            comment="x" * 1001,
        )


def test_configuration_value_objects_validate_bounds_and_secrets() -> None:
    llm = LLMConfig(provider="ollama", model="phi3.5", endpoint="http://localhost")
    embedding = EmbeddingConfig(
        provider="ollama",
        model="nomic-embed-text",
        model_version="1",
        endpoint="http://localhost",
        dimensions=768,
        index_compat_id="ollama:nomic-embed-text:1",
    )
    retrieval = RetrievalConfig()
    chunking = ChunkingConfig()

    assert not llm.api_key_configured
    assert embedding.dimensions == 768
    assert retrieval.final_top_k <= retrieval.top_k_candidates
    assert chunking.overlap_tokens < chunking.max_chunk_tokens
    with pytest.raises(ValueError):
        RetrievalConfig(dense_weight=0.8, sparse_weight=0.8)


def test_non_framework_domain_models_are_dataclasses() -> None:
    assert hasattr(Document, "__dataclass_fields__")
    assert hasattr(IngestionJob, "__dataclass_fields__")