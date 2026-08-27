# Constitution Compliance Checklist

Use this checklist during implementation review.

## Grounding and RAG

- [ ] Answers use only retrieved knowledge-base evidence.
- [ ] Supported answers include validated source citations.
- [ ] Insufficient evidence produces an explicit insufficient-information response.
- [ ] Retrieved documents are framed as passive reference material.
- [ ] LLM, embedding, parser, vector-store, and reranker integrations remain behind ports.

## Security and Privacy

- [ ] Secrets are externalized and never committed or logged.
- [ ] Uploads enforce type, signature, size, integrity, and path-safety checks.
- [ ] User-facing errors omit stack traces and infrastructure details.
- [ ] User and document prompt-injection attempts cannot change system behavior.
- [ ] No sensitive document content or unnecessary user query content is logged.

## Safety Boundary

- [ ] No tool-execution or autonomous external-system capability is introduced.
- [ ] No FLEXCUBE transaction, SQL, shell, production, or JIRA mutation capability exists.
- [ ] Feedback does not automatically modify prompts, models, retrieval, or the knowledge base.

## Architecture and Quality

- [ ] Domain remains free of frameworks, SDKs, and infrastructure imports.
- [ ] Application code depends on domain abstractions, not concrete adapters.
- [ ] API contracts are versioned, explicit, validated, and documented.
- [ ] Focused unit, integration, API, frontend, and RAG evaluation coverage is maintained.
