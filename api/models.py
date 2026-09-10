from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    category: str | None = None
    max_distance: float | None = None


class IngestRequest(BaseModel):
    file_path: str


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