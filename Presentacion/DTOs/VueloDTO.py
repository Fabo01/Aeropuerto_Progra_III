from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VueloDTO(BaseModel):
    id: Optional[int]
    numero_vuelo: str
    origen: str
    destino: str
    hora_salida: datetime
    hora_llegada: datetime
    prioridad: Optional[int] = 0  # Prioridad del vuelo (0 por defecto) desde el 0 hasta el 100, siendo 100 la mayor prioridad
    estado: Optional[str] = 'programado'  # Estado del vuelo
    emergencia: Optional[bool] = False

    class Config:
        from_attributes = True

