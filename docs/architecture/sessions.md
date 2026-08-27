# Session Privacy and Conversation Context

Chat sessions are short-lived and exist only in the running application process in the
initial release. The session identifier is a capability token for that active process; it
is not an authenticated user identity. Session messages are never written to the relational
database, vector store, logs, or long-term user profile.

## Lifecycle

- `POST /api/v1/sessions` creates an active session and returns its expiry time.
- Each successful chat turn refreshes `last_active_at` and the configured inactivity TTL.
- A session that reaches its expiry is deleted, including its messages. Subsequent use returns
  `SESSION_NOT_FOUND` with HTTP 404 and the client can start a new session.
- `DELETE /api/v1/sessions/{session_id}` explicitly deletes the session and all messages.
  Reusing that identifier returns `SESSION_NOT_FOUND`.

The lifecycle limits are configured with `SESSION_TTL_MINUTES`,
`SESSION_HISTORY_WINDOW_TURNS`, and `SESSION_HISTORY_TOKEN_BUDGET`. The server retains at most
the configured recent complete turns and selects only turns that fit the token budget. The
frontend also limits its visible message list to the same default-sized bounded window.

## Follow-up Resolution

The resolver may use recent user and assistant messages to rewrite references such as `it`,
`that screen`, and `the previous task code` into a retrieval query. If the history contains
multiple possible identifiers, the reference remains unresolved and is marked ambiguous rather
than silently selecting one.

History is context only. It is framed separately from `REFERENCE MATERIAL` in the LLM prompt,
and it can never create a citation or satisfy evidence sufficiency. Every question, including
every resolved follow-up, invokes the retriever with a fresh query. Citation validation and the
evidence-sufficiency policy then run unchanged against that request's retrieved chunks.

## Retention and Clearing

Clearing or expiry removes the server-side session and its in-memory message list. A new session
starts with no conversational context. This initial non-persistent design intentionally does not
provide history recovery across process restarts; durable session history is deferred.