# Security Injection Evaluation

**Feature**: 002-flexcube-support-chatbot
**Scope**: Phase 13 deterministic security fixtures

## Fixture Coverage

`backend/tests/eval/security_cases.json` covers direct and indirect injection, encoded
input, role confusion, prompt disclosure, configuration disclosure, command execution,
general-knowledge bypass, fabricated citations, mixed legitimate FLEXCUBE intent, and
benign uses of `ignore`, `system`, `configuration`, and `instructions`.

## Deterministic Results

The Phase 13 focused backend suite executed 32 tests successfully. It covered seven query
categories, encoded input, four benign false-positive cases, standalone refusal, eight
response-disclosure categories, document framing, storage passivity, API replacement,
raw-output replacement, and API refusal. The full backend suite executed 190 tests, including
all grounding, citation, evidence-sufficiency, session, multi-source, lifecycle, feedback,
failure, degraded-mode, and architecture regressions.

The full frontend Vitest suite executed 38 tests successfully, including four non-disclosure
tests covering model output, internal errors, ordinary FLEXCUBE terminology, and unsafe API
error payloads.

These are deterministic boundary-test results, not a measure of model capability or
production attack prevalence.

## Human Review

Human adversarial review has not been run. No human-review success rate is claimed here.
The fixture set is ready for review by two FLEXCUBE L1 support or security reviewers, with
disagreements resolved by adjudication before any groundedness or attack-resistance rate is
reported.
