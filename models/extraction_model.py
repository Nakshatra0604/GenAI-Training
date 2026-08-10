from pydantic import BaseModel


class ExtractionOutput(BaseModel):
    name: str
    email: str
    phone_number: str
    organization: str