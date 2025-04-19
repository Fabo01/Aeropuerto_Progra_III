from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from Config.db import get_db
from Presentacion.DTOs.VueloDTO import VueloDTO
from Servicios.VueloServicio import VueloServicio

router = APIRouter(
    prefix="/vuelos",
    tags=["vuelos"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=VueloDTO, status_code=status.HTTP_201_CREATED)
def crear_vuelo(vuelo: VueloDTO, db: Session = Depends(get_db)):
    servicio = VueloServicio(db)
    try:
        return servicio.crear_vuelo(vuelo)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[VueloDTO])
def obtener_vuelos(db: Session = Depends(get_db)):
    servicio = VueloServicio(db)
    return servicio.obtener_vuelos()

@router.get("/{vuelo_id}", response_model=VueloDTO)
def obtener_vuelo(vuelo_id: int, db: Session = Depends(get_db)):
    servicio = VueloServicio(db)
    vuelo = servicio.obtener_vuelo_por_id(vuelo_id)
    if not vuelo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return vuelo

@router.put("/{vuelo_id}", response_model=VueloDTO)
def actualizar_vuelo(vuelo_id: int, vuelo: VueloDTO, db: Session = Depends(get_db)):
    servicio = VueloServicio(db)
    vuelo_actualizado = servicio.actualizar_vuelo(vuelo_id, vuelo)
    if not vuelo_actualizado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return vuelo_actualizado

@router.delete("/{vuelo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vuelo(vuelo_id: int, db: Session = Depends(get_db)):
    servicio = VueloServicio(db)
    if not servicio.eliminar_vuelo(vuelo_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vuelo no encontrado")
    return {"message": "Vuelo eliminado correctamente"}
