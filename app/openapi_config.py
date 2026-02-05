from fastapi.openapi.utils import get_openapi
import os

PROJECT_NAME = os.environ.get("PROJECT_NAME")

def set_openapi_config(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=f"{PROJECT_NAME} API",
        version="1.0.0",
        description=f"OpenAPI schema for {PROJECT_NAME}",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema