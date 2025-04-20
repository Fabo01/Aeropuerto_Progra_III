from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VueloCreadoDTO(BaseModel):
    """DTO para crear un nuevo vuelo (sin ID)"""
    numero_vuelo: str
    origen: str
    destino: str
    hora_salida: datetime
    hora_llegada: datetime
    prioridad: Optional[int] = 0
    estado: Optional[str] = 'programado'
    emergencia: Optional[bool] = False

    class Config:
        from_attributes = True
