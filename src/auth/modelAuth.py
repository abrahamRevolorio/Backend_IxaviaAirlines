from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    accessToken: str
    tokenType: str

class TokenData(BaseModel):
    email: str | None = None
    userId: int | None = None
    role: str | None = None
