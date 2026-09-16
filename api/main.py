from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.dependencies import (
    check_generation_readiness,
    check_vector_store_readiness
)

from api.models import HealthResponse

from api.routes import router
from api.errors import ProviderError


app = FastAPI(
    title="GenAI RAG API",
    description="API for document ingestion and grounded question answering.",
    version="1.0.0"
)

@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError):
    request_id = request.headers.get("X-Request-ID")

    return JSONResponse(
        status_code=502,
        content={
            "error_code": "PROVIDER_ERROR",
            "message": "The AI provider is temporarily unavailable.",
            "request_id": request_id
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    error_code_map = {
        400: "INVALID_DOCUMENT",
        404: "DOCUMENT_NOT_FOUND",
        500: "INTERNAL_ERROR",
    }

    error_code = error_code_map.get(
        exc.status_code,
        "INTERNAL_ERROR"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": error_code,
            "message": str(exc.detail),
            "request_id": request.headers.get("X-Request-ID")
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request input.",
            "request_id": request.headers.get("X-Request-ID")
        }
    )


@app.exception_handler(Exception)
async def internal_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An unexpected internal error occurred.",
            "request_id": request.headers.get("X-Request-ID")
        }
    )


@app.get(
    "/health",
    response_model=HealthResponse
)
def health_check():
    generation_status = check_generation_readiness()
    vector_store_status = check_vector_store_readiness()

    dependencies = {
        "generation_model": generation_status,
        "vector_store": vector_store_status
    }

    if all(
        status == "ready"
        for status in dependencies.values()
    ):
        service_status = "healthy"
    else:
        service_status = "not_ready"

    return {
        "status": service_status,
        "dependencies": dependencies
    }


app.include_router(router)