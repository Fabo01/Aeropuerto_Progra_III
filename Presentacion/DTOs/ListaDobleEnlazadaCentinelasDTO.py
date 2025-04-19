from pydantic import BaseModel
from typing import Optional
from Presentacion.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO
from typing import List

class ListaDobleEnlazadaCentinelasDTO(BaseModel):
    id: Optional[int]
    nombre: str
    tamanio: int
    cabezon_id: int
    colon_id: int

    class Config:
        from_attributes = True

class ListaConNodosDTO(ListaDobleEnlazadaCentinelasDTO):
    nodos: List[NodoDobleVueloDTO] = []

    class Config:
        from_attributes = True