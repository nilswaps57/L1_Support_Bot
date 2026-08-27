# ADR-016: Bounded Session Context

**Status:** Accepted

## Decision

Keep session history in a bounded, expiring session store. History may resolve follow-up intent
and provide conversational context, but every domain answer performs fresh retrieval and uses
retrieved chunks as the sole evidence.

## Consequences

Clear and expiry remove context, and token budgets bound prompt growth. Long-term profiles and
cross-session retention remain out of scope.
