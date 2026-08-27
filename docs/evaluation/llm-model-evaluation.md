# LLM Model Evaluation

**Status:** blocked pending representative reviewed FLEXCUBE questions and candidate availability
**Review date:** 2026-08-27

## Required comparison

The same grounded FLEXCUBE question set, retrieval configuration, context budget, prompt, and
citation validator must be used for suitable Qwen, DeepSeek, Gemma, and Mistral variants available
through the configured Ollama-compatible provider. Compare correctness, groundedness, citation
compliance, insufficient-information behavior, prompt-injection resistance, latency, context
limits, hardware use, licensing, and compatibility.

Development baselines are separate from production selection: `qwen2.5:0.5b` and `phi3.5` may
help validate the pipeline but cannot be selected solely because they are installed.

## Availability observed

- Ollama is reachable at the local endpoint.
- Installed models are `qwen2.5:0.5b` and `nomic-embed-text:latest`.
- No DeepSeek, Gemma, Mistral, larger Qwen candidate, or `phi3.5` model is installed.
- No representative reviewed FLEXCUBE question set is available in the workspace.

## Results

No candidate result is reported. Without the reviewed corpus and comparable model set, correctness,
groundedness, citation, insufficient-information, injection, latency, hardware, context,
licensing, and Ollama compatibility measurements would be fabricated.

| Candidate family | Available | Evaluation result | Disposition |
|---|---:|---|---|
| Qwen | `qwen2.5:0.5b` development baseline only | Not run: reviewed corpus unavailable | No production selection |
| DeepSeek | No | Not evaluated | Install only through approved provider, then measure |
| Gemma | No | Not evaluated | Install only through approved provider, then measure |
| Mistral | No | Not evaluated | Install only through approved provider, then measure |
| phi3.5 | No | Not evaluated | Development baseline only |

## Required follow-up

Acquire the approved reviewed corpus and candidate models, run identical cases with saved
configuration snapshots, obtain two independent reviewer assessments, and record measured results.
Recommend a model provisionally only after those results; reconsider it when hardware, corpus,
license terms, context requirements, or provider changes.
