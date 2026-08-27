# LLM Integration

Phase 5 uses the `LLMPort` protocol and an infrastructure-only Ollama HTTP adapter. Requests
use Ollama's JSON response mode and pass a prompt created from explicitly framed retrieved
reference chunks. The adapter maps HTTP, timeout, malformed-response, and empty-response
failures to a safe `LLM_UNAVAILABLE` error. It never accesses Qdrant or any vector-store
client.

Live Ollama checks are opt-in. Automated tests use `httpx.MockTransport` and deterministic
responses.
