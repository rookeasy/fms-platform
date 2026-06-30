from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class PlaceholderResponse(BaseModel):
    module: str
    status: str = "placeholder"
    message: str
