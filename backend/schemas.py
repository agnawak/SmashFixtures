from pydantic import BaseModel, Field


class AuthRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class AuthResponse(BaseModel):
    api_key: str
    username: str


class SignupResponse(BaseModel):
    message: str
    api_key: str
    username: str
