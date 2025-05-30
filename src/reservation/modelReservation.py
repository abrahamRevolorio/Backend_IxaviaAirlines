from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict

class ReservationCreate(BaseModel):
    asiento_id: int
    vuelo_id: int

class ReservationInfo(BaseModel):
    asiento_id: int
    vuelo_id: int
    cliente_id: Optional[int]

class ReservationResponse(BaseModel):
    success: bool
    message: str
    reservation_info: Optional[ReservationInfo] = None
    status_code: int=200

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "El vuelo se ha registrado correctamente",
                "reservation_info": {
                    "asiento_id": 1,
                    "vuelo_id": 1,
                    "cliente_id": 1
                },
                "status_code": 201
            }
        }

class ReservationResponseList(BaseModel):
    success: bool
    message: str
    reservation_info: Optional[list[Dict[str, str]]] = None
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Consulta exitosa",
                "reservation_info": {
                    "asiento_id": 1,
                    "vuelo_id": 1,
                    "cliente_id": 1
                }
            }
        }