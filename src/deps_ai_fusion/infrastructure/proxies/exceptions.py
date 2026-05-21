from deps_ai_fusion.domain.exceptions import AiFusionError

__all__ = [
    "RestClientError",
    "ExtractionProxyError",
    "FileStorageProxyError",
    "UnifierProxyError",
    "ParsingProxyError",
]


class RestClientError(AiFusionError):
    code = "rest_client_error"


class ExtractionProxyError(RestClientError):
    code = "extraction_proxy_error"


class FileStorageProxyError(RestClientError):
    code = "file_storage_proxy_error"


class UnifierProxyError(RestClientError):
    code = "unifier_proxy_error"


class ParsingProxyError(RestClientError):
    code = "parsing_proxy_error"
