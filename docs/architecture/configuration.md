# Runtime Configuration

Phase 14 manages four configuration categories: LLM provider/model settings, embedding provider/model and vector compatibility settings, retrieval settings, and structure-aware chunking settings. Reranking remains configurable only through the existing retrieval model and is disabled unless an evaluated configuration enables it.

## Precedence and Snapshots

The runtime cache is initialized from environment-backed development defaults, then refreshed from the active relational configuration. A successful relational refresh replaces the cache atomically by category. A request captures one immutable `ConfigurationSnapshot` before retrieval or generation begins, so an in-flight request continues with the settings it started with. New requests see an activated snapshot only after a successful transaction and cache refresh.

GET responses expose only non-secret provider and model identifiers and approved numeric settings. Sensitive endpoint references, configuration IDs, API keys, passwords, tokens, and secret values are never returned to the frontend. A write may supply a new endpoint reference or a write-only secret field; the backend never stores raw secret values in ordinary configuration tables. Existing values are retained when a write omits an endpoint, and masked placeholders are not sent by the UI.

## Validation and Activation

LLM and embedding values are validated by domain value objects before persistence. Connectivity checks use each configuration's bounded timeout. Validation failures, unreachable endpoints, timeouts, authentication failures, malformed responses, and incompatible dimensions leave the active configuration unchanged. Retrieval thresholds and weights, retry limits, token limits, dimensions, chunk bounds, and overlap are validated before activation.

A complete four-category snapshot is written in one relational transaction. Existing active rows are deactivated and the replacement rows are inserted together. If persistence fails, the transaction rolls back and the last valid active snapshot remains in place. Configuration writes are blocked while authoritative relational persistence is unavailable; cached values are read-only in degraded mode.

## Index Compatibility

An embedding compatibility identity includes provider, model, version, and dimensions. Any identity change, or any chunking change that can alter chunk boundaries, requires a successful replacement index. The API returns `REINDEX_REQUIRED` and does not activate the incompatible configuration while indexed documents exist. The current compatible configuration and index remain usable; no full re-index is triggered automatically. The UI requires an explicit confirmation acknowledgement before submitting such a change, and still displays the backend decision rather than implying activation.

Retrieval-only settings and validated LLM provider/model changes may be hot-reloaded. Embedding and chunking changes are not hot-reloaded against an incompatible index. Settings outside the supported categories, production model selection, and deployment configuration are intentionally out of scope for Phase 14.
