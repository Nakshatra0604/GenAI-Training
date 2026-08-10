from pydantic import BaseModel, Field
from typing import List

class SummarizationOutput(BaseModel):
    summary_points: List[str] = Field(
        ...,
        min_length=5,
        max_length=5,
        description="Exactly 5 summary bullet points."
    )