from pydantic import BaseModel, Field
from typing import Optional


class SignUpRequest(BaseModel):
    name: str = Field(..., example="Jane Farmer")
    phone: str = Field(..., example="+254712345678")
    county: str = Field(..., example="Kajiado")
    subcounty: Optional[str] = Field(None, example="Loitokitok")
    produce: str = Field(..., example="maize")
    quantity: float = Field(..., example=100.0)
    password: str = Field(..., min_length=6)


class SignInRequest(BaseModel):
    phone: str = Field(..., example="+254712345678")
    password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    user_id: Optional[str] = None
    job_id: Optional[str] = None
