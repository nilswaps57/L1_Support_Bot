from datetime import UTC, datetime
from uuid import uuid4

from l1_support_bot.application.session.query_resolution import QueryResolution
from l1_support_bot.domain.models.session import ChatMessage, MessageRole


def message(role: MessageRole, content: str, order: int) -> ChatMessage:
    return ChatMessage(uuid4(), role, content, order, datetime.now(UTC))


def test_resolves_pronoun_to_the_latest_task_code() -> None:
    history = (
        message(MessageRole.USER, "What is task code BA435?", 0),
        message(MessageRole.ASSISTANT, "BA435 opens the customer account screen.", 1),
    )

    resolved = QueryResolution().resolve("What are its prerequisites?", history)

    assert resolved.is_follow_up is True
    assert "BA435" in resolved.retrieval_query


def test_resolves_screen_reference_from_previous_turn() -> None:
    history = (
        message(MessageRole.USER, "How do I use the Customer Account screen?", 0),
        message(MessageRole.ASSISTANT, "The Customer Account screen is used for accounts.", 1),
    )

    resolved = QueryResolution().resolve("What fields does that screen require?", history)

    assert "Customer Account screen" in resolved.retrieval_query


def test_resolves_previous_task_code_reference() -> None:
    history = (message(MessageRole.USER, "Explain task code ST123.", 0),)

    resolved = QueryResolution().resolve("Repeat the previous task code's menu path.", history)

    assert "ST123" in resolved.retrieval_query


def test_leaves_ambiguous_reference_unresolved() -> None:
    history = (
        message(MessageRole.USER, "Compare task codes BA435 and ST123.", 0),
        message(MessageRole.ASSISTANT, "Both task codes are documented.", 1),
    )

    resolved = QueryResolution().resolve("What are its prerequisites?", history)

    assert resolved.ambiguous is True
    assert resolved.retrieval_query == "What are its prerequisites?"


def test_history_selection_respects_turn_window_and_token_budget() -> None:
    history = tuple(
        item
        for turn in range(4)
        for item in (
            message(MessageRole.USER, f"question {turn} with several words", turn * 2),
            message(MessageRole.ASSISTANT, f"answer {turn} with several words", turn * 2 + 1),
        )
    )

    selected = QueryResolution(history_window_turns=3, token_budget=12).select_history(history)

    assert len(selected) <= 6
    assert sum(QueryResolution.estimate_tokens(item.content) for item in selected) <= 12
    assert selected[-1].content == "answer 3 with several words"


def test_without_history_a_reference_remains_a_fresh_query() -> None:
    resolved = QueryResolution().resolve("What are its prerequisites?", ())

    assert resolved.is_follow_up is False
    assert resolved.retrieval_query == "What are its prerequisites?"