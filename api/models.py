from pydantic import BaseModel, Field


class AskRequest(BaseModel):

    question: str = Field(
        min_length=1,
        max_length=2000
    )

    category: str | None = Field(
        default=None,
        max_length=100
    )

    max_distance: float | None = Field(
        default=None,
        ge=0
    )


class IngestRequest(BaseModel):

    file_path: str = Field(
        min_length=1
    )


class IngestResponse(BaseModel):

    document_id: str
    chunk_count: int
    status: str


class DocumentResponse(BaseModel):

    document_id: str
    title: str
    source_path: str
    updated_at: float
    category: str
    chunk_count: int
    status: str


class HealthResponse(BaseModel):

    status: str
    dependencies: dict[str, str]


class ErrorResponse(BaseModel):

    error_code: str
    message: str
    request_id: str | None = None