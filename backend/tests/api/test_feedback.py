import asyncio
from uuid import uuid4

from fastapi.testclient import TestClient

from l1_support_bot.domain.models.answer import Answer, AnswerType
from l1_support_bot.domain.models.citation import Citation
from l1_support_bot.domain.models.feedback import Feedback
from l1_support_bot.interface.api.main import create_app
from l1_support_bot.interface.dependencies import PortDependencies


class FeedbackStore:
    def __init__(self) -> None:
        self.saved: list[Feedback] = []
        self.contexts = {}

    async def save(self, feedback: Feedback) -> Feedback:
        self.saved.append(feedback)
        return feedback

    async def list_by_session(self, session_id):
        return tuple(item for item in self.saved if item.session_id == session_id)

    async def list_by_answer(self, answer_id):
        return tuple(item for item in self.saved if item.answer_id == answer_id)
    async def get_by_answer(self, answer_id):
        rows = await self.list_by_answer(answer_id)
        return rows[0] if rows else None

    async def save_answer_context(self, session_id, answer):
        self.contexts[(session_id, answer.answer_id)] = answer

    async def get_answer_context(self, session_id, answer_id):
        return self.contexts.get((session_id, answer_id))


def test_feedback_api_uses_authoritative_answer_context_and_is_idempotent() -> None:
    answer_id = uuid4()
    session_id = uuid4()
    chunk_id = uuid4()
    answer = Answer(
        answer_id=answer_id,
        question="What is BA435?",
        answer_text="It opens the account screen.",
        answer_type=AnswerType.GROUNDED,
        citations=(
            Citation(
                chunk_id=chunk_id,
                document_id=uuid4(),
                document_name="manual.pdf",
            ),
        ),
    )
    store = FeedbackStore()
    app = create_app(
        dependencies=PortDependencies(feedback_repository=store, session_store=store)
    )
    asyncio.run(store.save_answer_context(session_id, answer))
    client = TestClient(app)

    body = {
        "session_id": str(session_id),
        "answer_id": str(answer_id),
        "question": "frontend forgery",
        "answer_text": "frontend forgery",
        "rating": "helpful",
        "comment": "Good",
    }
    response = client.post("/api/v1/feedback", json=body)
    duplicate = client.post("/api/v1/feedback", json=body)

    assert response.status_code == 201
    assert duplicate.status_code == 200
    assert response.json()["feedback_id"] == duplicate.json()["feedback_id"]
    assert len(store.saved) == 1
    assert store.saved[0].question == answer.question
    assert store.saved[0].answer_text == answer.answer_text
    assert store.saved[0].retrieved_chunk_ids == (chunk_id,)
    assert asyncio.run(store.get_answer_context(session_id, answer_id)) == answer


def test_feedback_api_rejects_invalid_rating_and_comment() -> None:
    client = TestClient(create_app(dependencies=PortDependencies()))

    response = client.post(
        "/api/v1/feedback",
        json={"answer_id": str(uuid4()), "rating": "unknown", "comment": "x" * 1001},
    )

    assert response.status_code == 422