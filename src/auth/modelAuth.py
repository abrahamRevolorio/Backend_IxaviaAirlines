from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Dict

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

class UserRegister(BaseModel):

    email: EmailStr
    password: str

    dpi: str = Field(..., min_length=13, max_length=13)
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., min_length=8, max_length=8)
    direccion: str = Field(..., min_length=5, max_length=500)
    nacimiento: date
    nacionalidad: str = Field(..., min_length=3, max_length=100)
    telefonoEmergencia: str = Field(..., min_length=8, max_length=8)

    @field_validator("telefono", "telefonoEmergencia")
    @classmethod
    def validatePhone(cls, v):
        if not v.isdigit():
            raise ValueError("El telefono debe ser un numero")
        return v
    
    @field_validator("dpi")
    @classmethod
    def validateDpi(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El DPI debe ser un numero")
        return v

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user_info: Dict[str, str] | None = None
    status_code: int=200

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "El usuario se ha registrado correctamente",
                "user_info": {
                    "email": "OyO4S@example.com",
                    "nombres": "Juan",
                    "apellidos": "Pérez",
                },
                "status_code": 201
            }
        }
