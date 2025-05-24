from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Dict, Optional

class EmployerRegister(BaseModel):

    email: EmailStr
    password: str

    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    dpi: str = Field(..., min_length=13, max_length=13)
    nit : str = Field(..., min_length=13, max_length=13)
    telefono: str = Field(..., min_length=8, max_length=8)
    edad: int
    rol: str = Field(..., min_length=2, max_length=100)

    @field_validator("telefono")
    @classmethod
    def validatePhone(cls, v):
        if not v.isdigit():
            raise ValueError("El telefono debe ser un numero")
        return v
    
    @field_validator("dpi", "nit")
    @classmethod
    def validateDpi(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El DPI debe ser un numero")
        return v

class ClientRegister(BaseModel):
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
    rol: str = Field(..., min_length=2, max_length=100)

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

class FindUser(BaseModel):
    dpi: str = Field(..., min_length=13, max_length=13)

    @field_validator("dpi")
    @classmethod
    def validateDpi(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El DPI debe ser un numero")
        return v
    
class DeleteUser(BaseModel):
    dpi: str = Field(..., min_length=13, max_length=13)

    @field_validator("dpi")
    @classmethod
    def validateDpi(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El DPI debe ser un numero")
        return v
    
class UpdateUser(BaseModel):

    dpi: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    nacimiento: Optional[date] = None
    nacionalidad: Optional[str] = None
    telefonoEmergencia: Optional[str] = None
    nit: Optional[str] = None
    edad: Optional[int] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None