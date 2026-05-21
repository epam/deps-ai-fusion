from .base import AiFusionError, AlreadyExistsError, BusinessError, NotFoundError

__all__ = [
    "LLMExtractorNotFoundError",
    "QueryAlreadyExistsError",
    "QueryNotFoundError",
    "LLMExtractorError",
    "InvariantViolationError",
]


class LLMExtractorNotFoundError(NotFoundError):
    def __init__(self, id_: str, tenant_id: str) -> None:
        super().__init__(f"LLM Extractor not found for id='{id_}', {tenant_id=}")


class QueryAlreadyExistsError(AlreadyExistsError):
    def __init__(self, code: str, extractor_id: str, tenant_id: str) -> None:
        super().__init__(
            f"Query already exists with {code=} for LLM Extractor {extractor_id=}, {tenant_id=}",
        )


class QueryNotFoundError(NotFoundError):
    def __init__(self, code: str, extractor_id: str, tenant_id: str) -> None:
        super().__init__(
            f"Query not found with {code=} for LLM Extractor {extractor_id=}, {tenant_id=}",
        )


class LLMExtractorError(AiFusionError):
    code = "llm_extractor_error"

    def __init__(self, code: str | None = None, message: str | None = None) -> None:
        self.code = code or self.code
        if message:
            super().__init__(message)


class InvariantViolationError(BusinessError):
    code = "invariant_violation_error"

    def __init__(self, details: str) -> None:
        message = f"Invariant violation occurred: {details}"
        super().__init__(message)
        self.details = details
