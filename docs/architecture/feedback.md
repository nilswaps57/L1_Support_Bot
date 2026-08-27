# Feedback

Feedback is a supervised review signal attached to the exact answer shown to a user.
The chat response includes a backend-generated `answer_id`; the session store retains the
answer snapshot and its citation/configuration context for the feedback request. The API
uses that stored context rather than trusting question, answer, citation, or configuration
values from the browser.

Each submission records:

- the answer and applicable session identifiers
- the original question, answer text, and answer type
- the helpful or not-helpful rating and optional comment (at most 1,000 characters)
- cited/supporting chunk identifiers
- available LLM, embedding, and retrieval configuration identifiers
- the UTC submission timestamp

An answer accepts at most one feedback record. Repeated submissions for the same answer
return the original feedback identifier, so a repeated click cannot create duplicate review
records or change the original snapshot.

Feedback has no write path to documents, chunks, prompts, retrieval settings, model
configuration, or answer generation. It is retained for an explicit, supervised improvement
workflow only. The normal chatbot UI shows source citations first and presents feedback as
a secondary control; internal chunk and configuration identifiers are never displayed.