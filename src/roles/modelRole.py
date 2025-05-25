from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class RoleModel(BaseModel):
    nombrerol: str = Field(..., min_length=2, max_length=100)

class UpdateRole(BaseModel):
    rolid: Optional[int] = None
    nuevonombrerol: Optional[str] = None

class DeleteRole(BaseModel):
    rolid: Optional[int] = None
    
class RoleResponse(BaseModel):
    success: bool
    message: str
    status_code: int
    roles: Optional[Dict[str, str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "El rol se ha registrado correctamente",
                "status_code": 201
            }
        }