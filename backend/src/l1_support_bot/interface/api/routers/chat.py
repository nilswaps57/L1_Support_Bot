"""Grounded chat route for Phase 5."""

from fastapi import APIRouter, Request

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.domain.errors import ServiceUnavailableError
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.interface.dependencies import get_dependencies
from l1_support_bot.interface.dto.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(request: Request, payload: ChatRequest) -> ChatResponse:
    dependencies = get_dependencies(request)
    if dependencies.retriever is None or dependencies.llm is None:
        raise ServiceUnavailableError("Answer generation is temporarily unavailable.")
    settings = request.app.state.settings
    llm_config = LLMConfig(
        provider="ollama",
        model=settings.ollama_model,
        endpoint=settings.ollama_base_url,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    embedding_config = getattr(dependencies.retriever, "embedding_config", None)
    retrieval_config = RetrievalConfig()
    if embedding_config is None:
        raise ServiceUnavailableError("Answer retrieval is temporarily unavailable.")
    answer = await AskQuestion(
        retriever=dependencies.retriever,
        llm=dependencies.llm,
        llm_config=llm_config,
        retrieval_config=retrieval_config,
    ).execute(payload.question)
    return ChatResponse.from_answer(payload.session_id, answer)
