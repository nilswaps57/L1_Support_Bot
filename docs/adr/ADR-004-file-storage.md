# ADR-004: Local UUID-Based File Storage

**Status:** Accepted for local development

## Decision

Store validated source bytes in a configured local directory under UUID-based names. Verify
magic bytes and SHA-256, resolve paths within the storage root, and use atomic writes and cleanup.
The original filename is metadata only.

## Consequences

Path traversal and filename collisions are reduced without a new service. Storage is not a
production document-management architecture; retention, access control, backup, and encryption
must be decided before deployment.
