"""Safe domain error taxonomy shared by application and interface layers."""

from enum import StrEnum


class ErrorCategory(StrEnum):
    VALIDATION = "VALIDATION_ERROR"
    DUPLICATE = "DUPLICATE_DOCUMENT"
    PROCESSING = "PROCESSING_ERROR"
    UNAVAILABLE_SERVICE = "UNAVAILABLE_SERVICE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    INCOMPATIBLE_INDEX = "INCOMPATIBLE_INDEX"
    DOCUMENT_IN_PROCESSING = "DOCUMENT_IN_PROCESSING"
    DOCUMENT_CLEANUP_FAILED = "DOCUMENT_CLEANUP_FAILED"
    DOCUMENT_NOT_DELETABLE = "DOCUMENT_NOT_DELETABLE"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"


class DomainError(Exception):
    category = ErrorCategory.PROCESSING
    code = "DOMAIN_ERROR"

    def __init__(self, safe_message: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message
        self.details = details or {}


class ValidationError(DomainError):
    category = ErrorCategory.VALIDATION
    code = "VALIDATION_ERROR"


class CitationValidationError(ValidationError):
    code = "INVALID_CITATION"


class UnsupportedFileTypeError(ValidationError):
    code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(ValidationError):
    code = "FILE_TOO_LARGE"


class UnreadableFileError(ValidationError):
    code = "UNREADABLE_FILE"


class DuplicateDocumentError(DomainError):
    category = ErrorCategory.DUPLICATE
    code = "DUPLICATE_DOCUMENT"


class ProcessingError(DomainError):
    category = ErrorCategory.PROCESSING
    code = "PROCESSING_ERROR"


class ParserError(ProcessingError):
    code = "PARSER_ERROR"


class ParserUnavailableError(ProcessingError):
    code = "PARSER_UNAVAILABLE"


class ServiceUnavailableError(DomainError):
    category = ErrorCategory.UNAVAILABLE_SERVICE
    code = "SERVICE_UNAVAILABLE"


class RetryExhaustedError(ServiceUnavailableError):
    code = "RETRY_EXHAUSTED"

    def __init__(self) -> None:
        super().__init__("The requested service remains unavailable after a safe retry.")


class InsufficientEvidenceError(DomainError):
    category = ErrorCategory.INSUFFICIENT_EVIDENCE
    code = "INSUFFICIENT_EVIDENCE"

    def __init__(
        self,
        safe_message: str = "The available knowledge does not contain enough evidence.",
    ) -> None:
        super().__init__(safe_message)


class IncompatibleIndexError(DomainError):
    category = ErrorCategory.INCOMPATIBLE_INDEX
    code = "INCOMPATIBLE_INDEX"

    def __init__(
        self,
        safe_message: str = "The active embedding configuration is incompatible with the index.",
    ) -> None:
        super().__init__(safe_message)


class EmbeddingUnavailableError(ServiceUnavailableError):
    code = "EMBEDDING_UNAVAILABLE"

    def __init__(
        self, safe_message: str = "Embedding service is temporarily unavailable."
    ) -> None:
        super().__init__(safe_message)


class VectorStoreUnavailableError(ServiceUnavailableError):
    code = "VECTOR_STORE_UNAVAILABLE"

    def __init__(
        self, safe_message: str = "Vector search is temporarily unavailable."
    ) -> None:
        super().__init__(safe_message)


class LLMUnavailableError(ServiceUnavailableError):
    code = "LLM_UNAVAILABLE"

    def __init__(
        self, safe_message: str = "Answer generation is temporarily unavailable."
    ) -> None:
        super().__init__(safe_message)


class DatabaseUnavailableError(ServiceUnavailableError):
    code = "DATABASE_UNAVAILABLE"

    def __init__(
        self, safe_message: str = "Metadata persistence is temporarily unavailable."
    ) -> None:
        super().__init__(safe_message)


class ConfigurationConnectivityError(ValidationError):
    code = "CONFIGURATION_CONNECTIVITY_FAILED"


class LLMConnectivityError(ConfigurationConnectivityError):
    code = "LLM_CONNECTIVITY_FAILED"


class EmbeddingConnectivityError(ConfigurationConnectivityError):
    code = "EMBEDDING_CONNECTIVITY_FAILED"


class ReindexRequiredError(DomainError):
    category = ErrorCategory.INCOMPATIBLE_INDEX
    code = "REINDEX_REQUIRED"


class ConfigurationActivationError(DomainError):
    code = "CONFIGURATION_ACTIVATION_FAILED"


class DocumentInProcessingError(DomainError):
    category = ErrorCategory.DOCUMENT_IN_PROCESSING
    code = "DOCUMENT_IN_PROCESSING"


class DocumentNotDeletableError(DomainError):
    category = ErrorCategory.DOCUMENT_NOT_DELETABLE
    code = "DOCUMENT_NOT_DELETABLE"


class CleanupFailedError(DomainError):
    category = ErrorCategory.DOCUMENT_CLEANUP_FAILED
    code = "DOCUMENT_CLEANUP_FAILED"


class SessionNotFoundError(DomainError):
    code = "SESSION_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("The chat session was not found or has expired. Start a new session.")
