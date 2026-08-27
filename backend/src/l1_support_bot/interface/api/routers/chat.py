"""Grounded chat route for Phase 5."""

from fastapi import APIRouter, Request

from l1_support_bot.application.retrieval.ask_question import AskQuestion
from l1_support_bot.application.session.query_resolution import QueryResolution
from l1_support_bot.application.session.session_manager import SessionManager
from l1_support_bot.domain.errors import (
    DatabaseUnavailableError,
    DomainError,
    ServiceUnavailableError,
)
from l1_support_bot.domain.models.configuration import LLMConfig, RetrievalConfig
from l1_support_bot.interface.dependencies import get_dependencies
from l1_support_bot.interface.dto.chat import ChatRequest, ChatResponse
from l1_support_bot.interface.logging import log_security_event

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, response_model_exclude_none=True)
async def ask_question(request: Request, payload: ChatRequest) -> ChatResponse:
    dependencies = get_dependencies(request)
    if dependencies.retriever is None or dependencies.llm is None:
        raise ServiceUnavailableError("Answer generation is temporarily unavailable.")
    settings = request.app.state.settings
    cache = dependencies.runtime_configuration_cache
    degraded = False
    if cache is not None:
        try:
            await cache.refresh()
        except DatabaseUnavailableError:
            degraded = True
            health = getattr(cache, "health", None)
            if health is not None:
                health.mark_read_only_chat()
        except Exception as exc:
            raise DatabaseUnavailableError() from exc
    session_store = dependencies.session_store
    session_manager = (
        SessionManager(
            session_store,
            ttl_minutes=settings.session_ttl_minutes,
            history_window_turns=settings.session_history_window_turns,
            history_token_budget=settings.session_history_token_budget,
        )
        if session_store is not None
        else None
    )
    history = await session_manager.history(payload.session_id) if session_manager else ()
    resolution = QueryResolution(
        history_window_turns=settings.session_history_window_turns,
        token_budget=settings.session_history_token_budget,
    ).resolve(payload.question, history)
    snapshot = await cache.snapshot() if cache is not None else None
    llm_config = snapshot.llm if snapshot is not None else (
        await cache.get_llm()
        if cache is not None
        else LLMConfig(
            provider="ollama", model=settings.ollama_model,
            endpoint=settings.ollama_base_url, timeout_seconds=settings.ollama_timeout_seconds,
        )
    )
    if llm_config is None:
        raise ServiceUnavailableError("Answer generation is temporarily unavailable.")
    embedding_config = getattr(dependencies.retriever, "embedding_config", None)
    retrieval_config = snapshot.retrieval if snapshot is not None else (
        await cache.get_retrieval() if cache is not None else RetrievalConfig()
    ) or RetrievalConfig()
    if embedding_config is None:
        raise ServiceUnavailableError("Answer retrieval is temporarily unavailable.")
    try:
        answer = await AskQuestion(
            retriever=dependencies.retriever,
            llm=dependencies.llm,
            llm_config=llm_config,
            retrieval_config=retrieval_config,
            document_repository=None if degraded else dependencies.document_repository,
            reranker=dependencies.reranker,
            security_event_logger=log_security_event,
        ).execute(
            payload.question,
            retrieval_question=resolution.retrieval_query,
            conversation_context=resolution.history,
        )
    except DomainError as exc:
        if cache is not None:
            component = {
                "LLM_UNAVAILABLE": "llm",
                "VECTOR_STORE_UNAVAILABLE": "vector_store",
                "EMBEDDING_UNAVAILABLE": "embedding",
                "DATABASE_UNAVAILABLE": "database",
            }.get(exc.code)
            if component is not None:
                cache.mark_component_unavailable(component) if hasattr(
                    cache, "mark_component_unavailable"
                ) else None
        raise
    if session_manager is not None:
        await session_manager.record_turn(
            payload.session_id, payload.question, answer.answer_text, answer_context=answer
        )
    return ChatResponse.from_answer(payload.session_id, answer)
