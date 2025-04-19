from pydantic import BaseModel
from typing import Optional, List
from Presentacion.API.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO

class ListaDobleEnlazadaCentinelasDTO(BaseModel):
    id: Optional[int]
    nombre: str
    nodos: List[NodoDobleVueloDTO] = []

    class Config:
        from_attributes = True