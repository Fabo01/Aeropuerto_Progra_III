from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from Config.db import get_db
from Presentacion.DTOs.ListaDobleEnlazadaCentinelasDTO import ListaDobleEnlazadaCentinelasDTO, ListaConNodosDTO
from Presentacion.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO
from Presentacion.DTOs.VueloDTO import VueloDTO
from Servicios.ListaDobleEnlazadaServicio import ListaDobleEnlazadaServicio

router = APIRouter(
    prefix="/lista",  # Cambiado a singular para reflejar que solo hay una lista
    tags=["lista"],
    responses={404: {"description": "No encontrado"}},
)

@router.get("/", response_model=ListaConNodosDTO)
def obtener_lista_con_nodos(db: Session = Depends(get_db)):
    """Obtener la lista principal con todos sus nodos"""
    servicio = ListaDobleEnlazadaServicio(db)
    lista_con_nodos = servicio.obtener_lista_con_nodos()
    return lista_con_nodos

@router.post("/insertar-al-frente", response_model=NodoDobleVueloDTO)
def insertar_vuelo_al_frente(vuelo_id: int, db: Session = Depends(get_db)):
    """Inserta un vuelo al principio de la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    nodo = servicio.insertar_vuelo_al_frente(vuelo_id)
    if not nodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return nodo

@router.post("/insertar-al-final", response_model=NodoDobleVueloDTO)
def insertar_vuelo_al_final(vuelo_id: int, db: Session = Depends(get_db)):
    """Inserta un vuelo al final de la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    nodo = servicio.insertar_vuelo_al_final(vuelo_id)
    if not nodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return nodo

@router.post("/insertar-ordenado", response_model=NodoDobleVueloDTO)
def insertar_vuelo_ordenado(vuelo_id: int, posicion: Optional[int] = None, db: Session = Depends(get_db)):
    """
    Inserta un vuelo en la lista principal.
    Si se proporciona posición, se inserta en esa posición específica.
    Si no se proporciona posición, se ordena automáticamente por prioridad.
    """
    servicio = ListaDobleEnlazadaServicio(db)
    
    if posicion is not None:
        # Si se especifica posición, insertar en esa posición
        nodo = servicio.insertar_vuelo_en_posicion(vuelo_id, posicion)
    else:
        # Si no se especifica posición, ordenar por prioridad
        nodo = servicio.insertar_vuelo_ordenado_por_prioridad(vuelo_id)
        
    if not nodo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return nodo

@router.delete("/extraer/{posicion}", response_model=VueloDTO)
def extraer_vuelo_de_posicion(posicion: int, db: Session = Depends(get_db)):
    """Extrae un vuelo de una posición específica de la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    vuelo = servicio.extraer_vuelo_de_posicion(posicion)
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró un vuelo en esa posición")
    return vuelo

@router.post("/reordenar", status_code=status.HTTP_200_OK)
def reordenar_lista(db: Session = Depends(get_db)):
    """Reordena la lista principal según prioridad y estado de emergencia"""
    servicio = ListaDobleEnlazadaServicio(db)
    servicio.reordenar_lista_por_prioridad()
    return {"message": "Lista reordenada correctamente"}

@router.get("/cantidad", response_model=int)
def obtener_cantidad_nodos(db: Session = Depends(get_db)):
    """Obtiene la cantidad de nodos en la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    return servicio.obtener_cantidad_nodos()

@router.get("/primer-vuelo", response_model=VueloDTO)
def obtener_primer_vuelo(db: Session = Depends(get_db)):
    """Obtiene el primer vuelo de la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    vuelo = servicio.obtener_primer_vuelo()
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay vuelos en la lista")
    return vuelo

@router.get("/ultimo-vuelo", response_model=VueloDTO)
def obtener_ultimo_vuelo(db: Session = Depends(get_db)):
    """Obtiene el último vuelo de la lista principal"""
    servicio = ListaDobleEnlazadaServicio(db)
    vuelo = servicio.obtener_ultimo_vuelo()
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No hay vuelos en la lista")
    return vuelo

@router.post("/mover-nodo", status_code=status.HTTP_200_OK)
def mover_nodo_entre_posiciones(posicion_origen: int, posicion_destino: int, db: Session = Depends(get_db)):
    """
    Mueve un nodo de una posición a otra en la lista principal.
    Después del movimiento, todas las posiciones se actualizan para mantener la coherencia.
    """
    servicio = ListaDobleEnlazadaServicio(db)
    if servicio.mover_nodo_entre_posiciones(posicion_origen, posicion_destino):
        return {"message": f"Nodo movido correctamente de la posición {posicion_origen} a la posición {posicion_destino}"}
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, 
        detail=f"No se pudo mover el nodo de la posición {posicion_origen} a la posición {posicion_destino}"
    )
