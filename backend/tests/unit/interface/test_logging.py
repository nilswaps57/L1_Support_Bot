from uuid import UUID

from l1_support_bot.interface.logging import (
    RequestContext,
    bind_request_context,
    clear_request_context,
    get_request_context,
)


def test_request_context_contains_only_correlation_identifiers() -> None:
    request_id = "11111111-1111-4111-8111-111111111111"
    correlation_id = "22222222-2222-4222-8222-222222222222"

    bind_request_context(request_id=request_id, correlation_id=correlation_id)
    context = get_request_context()
    clear_request_context()

    assert context == RequestContext(UUID(request_id), UUID(correlation_id))
    assert get_request_context() is None