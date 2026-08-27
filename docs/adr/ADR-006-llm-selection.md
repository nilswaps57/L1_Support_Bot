# ADR-006: LLM Selection

**Status:** Provisional, evaluation blocked

## Decision

Keep the LLM behind `LLMPort` and the Ollama HTTP adapter. Do not select a production model from
installation state. The Phase 15 comparison must include suitable Qwen, DeepSeek, Gemma, and
Mistral variants, with `qwen2.5:0.5b` and `phi3.5` treated only as development baselines.

## Evidence status

Only `qwen2.5:0.5b` is installed locally, and no representative reviewed FLEXCUBE question set
is available. No correctness, groundedness, citation, injection, latency, hardware, context,
licensing, or compatibility result is claimed. T210 remains incomplete.

## Consequences

Model replacement requires configuration rather than application changes. Production selection
must be based on measured evidence and reconsidered when corpus, hardware, or provider changes.
