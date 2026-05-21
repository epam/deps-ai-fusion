import inspect

from fastapi.routing import APIRoute

__all__ = ["MarkerRoute"]


class MarkerRoute(APIRoute):
    def __init__(self, *args, **kwargs) -> None:
        if inspect.isroutine(kwargs["endpoint"]) or inspect.isclass(kwargs["endpoint"]):
            name = kwargs["endpoint"].__name__
        else:
            name = kwargs["endpoint"].__class__.__name__

        endpoint_name = name.replace("_", " ").title()

        if kwargs.get("openapi_extra"):
            visibility = kwargs["openapi_extra"]["visibility"]
            kwargs["summary"] = f"[{visibility.value}] {endpoint_name}"

        super().__init__(*args, **kwargs)
