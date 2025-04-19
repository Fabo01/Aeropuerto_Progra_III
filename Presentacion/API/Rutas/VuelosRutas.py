from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Presentacion.API.DTOs.VueloDTO import VueloDTO
from Presentacion.API.DTOs.ListaDobleEnlazadaCentinelasDTO import ListaDobleEnlazadaCentinelasDTO
from Presentacion.API.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO
from Modelos.Vuelo import Vuelo
from Servicios.VueloServicio import VueloServicio
from Repositorios.VueloRepositorio import VueloRepositorio
from Repositorios.ListaVuelosRepositorio import ListaVuelosRepositorio
from Config.db import get_db
from typing import List, Optional, Dict, Any
import logging

router = APIRouter(prefix="/vuelos", tags=["Vuelos"])

# Dependencia para obtener el servicio
def get_vuelo_servicio(db: Session = Depends(get_db)):
    return VueloServicio(VueloRepositorio(db))

# Dependencia para obtener el repositorio de lista de vuelos
def get_lista_vuelos_repo(db: Session = Depends(get_db)):
    return ListaVuelosRepositorio(db)

@router.post("/", response_model=VueloDTO)
def crear_vuelo(
    vuelo: VueloDTO,
    posicion: Optional[int] = None,
    servicio: VueloServicio = Depends(get_vuelo_servicio)
):
    """
    Crea un nuevo vuelo y lo añade a la lista según su prioridad y emergencia.
    
    Si es una emergencia, se insertará al frente de la lista.
    Si se especifica una posición, se insertará en esa posición.
    De lo contrario, se añadirá al final de la lista.
    """
    try:
        return servicio.crear_vuelo(vuelo, posicion=posicion)
    except Exception as e:
        logging.error(f"Error creating flight: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al crear vuelo: {str(e)}"
        )

@router.get("/", response_model=List[VueloDTO])
def obtener_vuelos(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Obtiene todos los vuelos ordenados según la lista"""
    try:
        return servicio.obtener_vuelos()
    except Exception as e:
        logging.error(f"Error retrieving flights: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener vuelos: {str(e)}"
        )

@router.get("/primero", response_model=VueloDTO)
def obtener_primero(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Obtiene el primer vuelo de la lista (próximo a despegar)"""
    vuelo = servicio.obtener_primero()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos")
    return vuelo

@router.get("/ultimo", response_model=VueloDTO)
def obtener_ultimo(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Obtiene el último vuelo de la lista"""
    vuelo = servicio.obtener_ultimo()
    if not vuelo:
        raise HTTPException(status_code=404, detail="No hay vuelos")
    return vuelo

@router.delete("/{posicion}", response_model=VueloDTO)
def cancelar_vuelo(posicion: int, servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Cancela (elimina) un vuelo de la lista y de la base de datos"""
    vuelo = servicio.cancelar_vuelo(posicion)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

@router.patch("/{vuelo_id}/estado", response_model=VueloDTO)
def actualizar_estado(vuelo_id: int, nuevo_estado: str, servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """
    Actualiza el estado de un vuelo
    
    Estados posibles: 'programado', 'retrasado', 'cancelado'
    """
    if nuevo_estado not in ['programado', 'retrasado', 'cancelado']:
        raise HTTPException(status_code=400, 
                           detail="Estado inválido. Use 'programado', 'retrasado' o 'cancelado'")
                           
    vuelo = servicio.actualizar_estado(vuelo_id, nuevo_estado)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

@router.patch("/mover/{posicion_origen}/{posicion_destino}")
def mover_vuelo(posicion_origen: int, posicion_destino: int, servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """
    Mueve un vuelo de una posición a otra en la lista
    
    Útil para reorganizar los vuelos cuando hay retrasos o prioridades cambiantes.
    """
    exito = servicio.mover_vuelo(posicion_origen, posicion_destino)
    if not exito:
        raise HTTPException(status_code=400, detail="No se pudo mover el vuelo. Verifica las posiciones.")
    return {"mensaje": f"Vuelo movido de {posicion_origen} a {posicion_destino}"}

@router.patch("/{vuelo_id}/emergencia", response_model=VueloDTO)
def actualizar_emergencia(
    vuelo_id: int, 
    es_emergencia: bool, 
    servicio: VueloServicio = Depends(get_vuelo_servicio)
):
    """
    Marca o desmarca un vuelo como emergencia
    
    Los vuelos de emergencia son automáticamente movidos al frente de la lista.
    """
    vuelo = servicio.marcar_emergencia(vuelo_id, es_emergencia)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

@router.patch("/{vuelo_id}/prioridad", response_model=VueloDTO)
def actualizar_prioridad(
    vuelo_id: int, 
    nueva_prioridad: int, 
    servicio: VueloServicio = Depends(get_vuelo_servicio)
):
    """
    Actualiza la prioridad de un vuelo (0-100)
    
    Mayor prioridad (más cercano a 100) significa un vuelo más importante.
    """
    if not (0 <= nueva_prioridad <= 100):
        raise HTTPException(
            status_code=400, 
            detail="Prioridad debe estar entre 0 y 100"
        )
        
    vuelo = servicio.actualizar_prioridad(vuelo_id, nueva_prioridad)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    return vuelo

@router.get("/historial", response_model=List[Dict[str, Any]])
def obtener_historial(
    limite: int = 10, 
    servicio: VueloServicio = Depends(get_vuelo_servicio)
):
    """Obtiene el historial de acciones realizadas en el sistema"""
    return servicio.obtener_historial_acciones(limite)

@router.post("/deshacer")
def deshacer_accion(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Deshace la última acción realizada"""
    exito, mensaje = servicio.deshacer()
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    return {"mensaje": mensaje}

@router.post("/rehacer")
def rehacer_accion(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Rehace la última acción deshecha"""
    exito, mensaje = servicio.rehacer()
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    return {"mensaje": mensaje}

@router.get("/longitud")
def obtener_longitud(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Obtiene el número total de vuelos en la lista"""
    return {"longitud": servicio.longitud()}

@router.post("/cargar_db")
def cargar_desde_db(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """Carga la lista de vuelos desde la base de datos"""
    servicio.cargar_desde_db()
    return {"mensaje": "Lista de vuelos cargada desde la base de datos"}

@router.get("/estructura_db")
def obtener_estructura_db(lista_repo: ListaVuelosRepositorio = Depends(get_lista_vuelos_repo)):
    """
    Obtiene información de la estructura persistente de la lista doblemente enlazada.
    Útil para verificar que la persistencia funciona correctamente.
    """
    estado = lista_repo.obtener_estado()
    if not estado:
        return {"mensaje": "La lista no está inicializada"}
    
    # Información básica
    resultado = {
        "nombre": estado.nombre,
        "tamanio": estado.tamanio,
        "cabezon_id": estado.cabezon_id,
        "colon_id": estado.colon_id,
    }
    
    # Obtener todos los vuelos en orden
    vuelos = lista_repo.obtener_todos()
    vuelos_info = []
    
    for i, vuelo in enumerate(vuelos):
        vuelos_info.append({
            "posicion": i,
            "id": vuelo.id,
            "numero_vuelo": vuelo.numero_vuelo,
            "origen": vuelo.origen,
            "destino": vuelo.destino,
            "emergencia": vuelo.emergencia,
            "prioridad": vuelo.prioridad
        })
    
    resultado["vuelos"] = vuelos_info
    return resultado

@router.post("/reiniciar_estructura")
def reiniciar_estructura_db(lista_repo: ListaVuelosRepositorio = Depends(get_lista_vuelos_repo)):
    """
    Reinicia la estructura persistente de la lista doblemente enlazada.
    Útil para solucionar problemas o realizar pruebas.
    """
    lista_repo.eliminar_lista()
    lista_repo.inicializar_lista()
    return {"mensaje": "Estructura de la lista reinicializada correctamente"}

@router.get("/estructura_dto", response_model=ListaDobleEnlazadaCentinelasDTO)
def obtener_estructura_dto(servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """
    Devuelve la estructura de la lista doblemente enlazada como DTO.
    """
    return servicio.obtener_lista_dto()

@router.get("/nodo/{nodo_id}", response_model=NodoDobleVueloDTO)
def obtener_nodo_dto(nodo_id: int, servicio: VueloServicio = Depends(get_vuelo_servicio)):
    """
    Devuelve un nodo de la lista como DTO.
    """
    nodo = servicio.obtener_nodo_dto(nodo_id)
    if not nodo:
        raise HTTPException(status_code=404, detail="Nodo no encontrado")
    return nodo
