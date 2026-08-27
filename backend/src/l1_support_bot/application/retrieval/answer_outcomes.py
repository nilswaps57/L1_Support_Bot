"""Safe, citation-aware answer outcome factories."""

from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.ports.vector_store import VectorSearchResult

INSUFFICIENT_MESSAGE = (
    "The available knowledge sources do not contain sufficient information to answer this question."
)


def insufficient_info_response(question: str, message: str = INSUFFICIENT_MESSAGE) -> Answer:
    return Answer(
        question=question,
        answer_text=message,
        answer_type=AnswerType.INSUFFICIENT,
        insufficient_information=True,
    )


def partial_answer(
    question: str,
    answer_text: str,
    citations: tuple[Citation, ...] = (),
    model_used: str | None = None,
) -> Answer:
    return Answer(
        question=question,
        answer_text=_explicit_partial_text(answer_text),
        answer_type=AnswerType.PARTIAL,
        citations=citations,
        model_used=model_used,
    )


def ambiguous_answer(
    question: str,
    answer_text: str,
    results: tuple[VectorSearchResult, ...] = (),
) -> Answer:
    candidates = _ambiguity_candidates(results)
    if candidates and not any(candidate.lower() in answer_text.lower() for candidate in candidates):
        answer_text = (
            f"{answer_text.rstrip()} Candidate interpretations found in the knowledge base: "
            f"{', '.join(candidates)}. Please clarify which one you mean."
        )
    return Answer(question=question, answer_text=answer_text, answer_type=AnswerType.AMBIGUOUS)


def incorrect_premise_answer(question: str, answer_text: str | None = None) -> Answer:
    return Answer(
        question=question,
        answer_text=answer_text
        or "The question's premise is not supported by the available knowledge sources.",
        answer_type=AnswerType.INCORRECT_PREMISE,
    )


class InsufficientInfoResponse:
    """Named response path retained for callers that need an explicit outcome type."""

    @staticmethod
    def create(question: str, message: str = INSUFFICIENT_MESSAGE) -> Answer:
        return insufficient_info_response(question, message)


def _explicit_partial_text(answer_text: str) -> str:
    markers = ("not cover", "does not include", "unsupported", "unknown", "unavailable")
    if any(marker in answer_text.lower() for marker in markers):
        return answer_text
    return (
        f"{answer_text.rstrip()} The available knowledge sources do not cover the remaining "
        "requested details."
    )


def _ambiguity_candidates(results: tuple[VectorSearchResult, ...]) -> tuple[str, ...]:
    candidates: list[str] = []
    for result in results:
        metadata = result.chunk.metadata
        for candidate in (
            metadata.screen_name,
            metadata.task_code,
            metadata.error_code,
            metadata.jira_id,
        ):
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return tuple(candidates)
