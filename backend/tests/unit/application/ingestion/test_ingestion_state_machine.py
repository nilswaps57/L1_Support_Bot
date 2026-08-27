from uuid import uuid4

import pytest

from l1_support_bot.domain.models.ingestion import IngestionJob, IngestionStatus


def test_pre_indexing_warning_is_not_queryable() -> None:
    assert not IngestionStatus.READY_FOR_INDEXING_WITH_WARNING.is_queryable
    job = IngestionJob.new(uuid4()).transition_to(IngestionStatus.PARSING)
    job = job.transition_to(IngestionStatus.NORMALISING)
    job = job.transition_to(IngestionStatus.CHUNKING)
    job = job.transition_to(IngestionStatus.READY_FOR_INDEXING_WITH_WARNING)

    assert job.status is IngestionStatus.READY_FOR_INDEXING_WITH_WARNING
    assert not job.status.is_queryable


def test_completed_warning_is_reserved_for_later_successful_indexing() -> None:
    job = IngestionJob.new(uuid4())
    for status in (
        IngestionStatus.PARSING,
        IngestionStatus.NORMALISING,
        IngestionStatus.CHUNKING,
        IngestionStatus.READY_FOR_INDEXING_WITH_WARNING,
        IngestionStatus.EMBEDDING,
        IngestionStatus.INDEXING,
    ):
        job = job.transition_to(status)
    job = job.transition_to(IngestionStatus.COMPLETED_WITH_WARNING)

    assert job.status.is_queryable


def test_invalid_transition_is_rejected() -> None:
    with pytest.raises(ValueError):
        IngestionJob.new(uuid4()).transition_to(IngestionStatus.COMPLETED)
