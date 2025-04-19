from pydantic import BaseModel
from typing import Optional
from Presentacion.DTOs.VueloDTO import VueloDTO

class NodoDobleVueloDTO(BaseModel):
    id: Optional[int]
    vuelo: VueloDTO
    posicion: int
    lista_id: int  # Relación con la lista doble
    anterior_id: Optional[int] = None
    siguiente_id: Optional[int] = None

    class Config:
        from_attributes = True