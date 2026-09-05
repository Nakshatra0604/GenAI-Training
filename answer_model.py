from pydantic import BaseModel
from typing import Literal

class AnswerResponse(BaseModel):
    answer:str
    sources: list[str]
    chunks: list[str]
    scores: list[float]
    status: Literal["answered", "insufficient_evidence"]
     
if __name__ == "__main__":

    response = AnswerResponse(
        answer="Software requests must follow the IT request process.",
        sources=[
            "DOC-009:it\\DOC-009_software_installation_request_process.md"
        ],
        chunks=[
            "If required software is not available in the standard IT catalog..."
        ],
        scores=[0.21],
        status="answered"
    )

    print(response)
