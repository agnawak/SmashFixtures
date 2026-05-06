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


class ChatMessage(BaseModel):
    role: str  # 'user' or 'model'
    text: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str
