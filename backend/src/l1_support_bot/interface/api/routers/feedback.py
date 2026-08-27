"""Feedback submission endpoint."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from l1_support_bot.application.feedback.submit_feedback import SubmitFeedback
from l1_support_bot.domain.errors import ServiceUnavailableError, ValidationError
from l1_support_bot.interface.dependencies import ensure_persistence_available, get_dependencies
from l1_support_bot.interface.dto.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, response_model_exclude_none=True)
async def submit_feedback(request: Request, payload: FeedbackRequest) -> JSONResponse:
    await ensure_persistence_available(request)
    dependencies = get_dependencies(request)
    repository = dependencies.feedback_repository
    store = dependencies.session_store
    if repository is None or store is None:
        raise ServiceUnavailableError("Feedback is temporarily unavailable.")
    answer = await store.get_answer_context(payload.session_id, payload.answer_id)
    if answer is None:
        raise ValidationError(
            "The answer is no longer available for feedback.",
        )
    existing = await repository.get_by_answer(payload.answer_id)
    feedback = await SubmitFeedback(repository).execute(
        answer=answer,
        session_id=payload.session_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    response = FeedbackResponse(feedback_id=feedback.id)
    return JSONResponse(
        status_code=200 if existing is not None else 201,
        content=response.model_dump(mode="json"),
    )