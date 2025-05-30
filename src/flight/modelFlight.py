from pydantic import BaseModel, Field, field_validator
from datetime import date, time
from typing import Optional, Dict

class FlightCreate(BaseModel):
    fecha: date
    hora_salida: str
    hora_llegada: str
    destino_id: int = Field(..., gt=0)
    avion_id: int = Field(..., gt=0)

    @field_validator("hora_salida", "hora_llegada")
    @classmethod
    def validate_time_format(cls, v):
        try:
            hours, minutes, seconds = map(int, v.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError
            return v
        except ValueError:
            raise ValueError("Formato de hora inválido. Use HH:MM:SS")

class FlightInfo(BaseModel):
    fecha: date
    hora_salida: time
    hora_llegada: time
    destino_id: int
    avion_id: int

class FlightResponse(BaseModel):
    success: bool
    message: str
    flight_info: Optional[FlightInfo] = None
    status_code: int=200

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "El vuelo se ha registrado correctamente",
                "flight_info": {
                    "id": 1,
                    "fecha": "2023-06-01",
                    "hora_salida": "10:00:00",
                    "hora_llegada": "12:00:00",
                    "destino_id": 1,
                    "avion_id": 1
                },
                "status_code": 201
            }
        }

class FlightResponseList(BaseModel):
    success: bool
    message: str
    flights_info: Optional[list[Dict[str, str]]] = None
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Consulta exitosa",
                "flights_info": {
                    "id": 1,
                    "fecha": "2023-06-01",
                    "hora_salida": "10:00:00",  
                    "hora_llegada": "12:00:00",
                    "destino_id": 1,
                    "avion_id": 1
                }
            }
        }

class FlightUpdate(BaseModel):
    fecha: Optional[date] = None
    hora_salida: Optional[str] = None
    hora_llegada: Optional[str] = None
    destino_id: Optional[int] = None
    avion_id: Optional[int] = None

    @field_validator("hora_salida", "hora_llegada")
    @classmethod
    def validate_time_format(cls, v):
        if v is None:
            return v
        try:
            hours, minutes, seconds = map(int, v.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60):
                raise ValueError
            return v
        except ValueError:
            raise ValueError("Formato de hora inválido. Use HH:MM:SS")