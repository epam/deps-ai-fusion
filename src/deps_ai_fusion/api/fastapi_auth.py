__all__ = ["add_auth_to_openapi"]


def add_auth_to_openapi(fastapi_app):
    from fastapi.openapi.utils import get_openapi

    security_schema = {
        "securitySchemes": {
            "Bearer Auth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
        },
    }

    def custom_openapi():
        if fastapi_app.openapi_schema:
            return fastapi_app.openapi_schema

        openapi_schema = get_openapi(
            title=fastapi_app.title,
            version=fastapi_app.version,
            routes=fastapi_app.routes,
        )

        schema_components = openapi_schema.get("components")
        if schema_components:
            openapi_schema["components"].update(security_schema)
        else:
            openapi_schema["components"] = security_schema

        openapi_schema["security"] = [{"Bearer Auth": []}]

        fastapi_app.openapi_schema = openapi_schema
        return fastapi_app.openapi_schema

    fastapi_app.openapi = custom_openapi
