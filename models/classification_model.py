from typing import Literal

from pydantic import BaseModel


class ClassificationOutput(BaseModel):
    label: Literal[
        "Technology",
        "Healthcare",
        "Finance",
        "Education"
    ]
    reason: str