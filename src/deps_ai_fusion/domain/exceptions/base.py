__all__ = ["AiFusionError", "NotFoundError", "IllegalArgument", "BusinessError", "AlreadyExistsError"]


class AiFusionError(Exception):
    code = "ai_fusion_exception"


class BusinessError(AiFusionError):
    code = "business_exception"


class NotFoundError(AiFusionError):
    code = "not_found_error"


class IllegalArgument(BusinessError):
    code = "illegal_argument"


class AlreadyExistsError(BusinessError):
    code = "already_exists_error"
