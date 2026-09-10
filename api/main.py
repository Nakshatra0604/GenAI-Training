from fastapi import FastAPI

from api.dependencies import (
    check_generation_readiness,
    check_vector_store_readiness
)

from api.models import HealthResponse

from api.routes import router


app = FastAPI(
    title="GenAI RAG API",
    description="API for document ingestion and grounded question answering.",
    version="1.0.0"
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