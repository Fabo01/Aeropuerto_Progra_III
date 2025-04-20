from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from Repositorios.VueloRepo import VueloRepo
from Dominio.Modelos.Vuelo import Vuelo
from Presentacion.DTOs.VueloDTO import VueloDTO
from Presentacion.DTOs.VueloCreadoDTO import VueloCreadoDTO

class VueloServicio:
    def __init__(self, db: Session):
        self.repo = VueloRepo(db)
        
    def crear_vuelo(self, vuelo_dto: Union[VueloDTO, VueloCreadoDTO]) -> VueloDTO:
        """Crea un nuevo vuelo en la base de datos"""
        vuelo = Vuelo(
            numero_vuelo=vuelo_dto.numero_vuelo,
            origen=vuelo_dto.origen,
            destino=vuelo_dto.destino,
            hora_salida=vuelo_dto.hora_salida,
            hora_llegada=vuelo_dto.hora_llegada,
            prioridad=vuelo_dto.prioridad,
            estado=vuelo_dto.estado,
            emergencia=vuelo_dto.emergencia
        )
        
        vuelo_creado = self.repo.crear_vuelo(vuelo)
        return self._vuelo_a_dto(vuelo_creado)
        
    def obtener_vuelos(self) -> List[VueloDTO]:
        """Obtiene todos los vuelos"""
        vuelos = self.repo.obtener_vuelos()
        return [self._vuelo_a_dto(vuelo) for vuelo in vuelos]
        
    def obtener_vuelo_por_id(self, vuelo_id: int) -> Optional[VueloDTO]:
        """Obtiene un vuelo por su ID"""
        vuelo = self.repo.obtener_vuelo_por_id(vuelo_id)
        if not vuelo:
            return None
        return self._vuelo_a_dto(vuelo)
        
    def obtener_vuelo_por_numero(self, numero_vuelo: str) -> Optional[VueloDTO]:
        """Obtiene un vuelo por su número"""
        vuelo = self.repo.obtener_vuelo_por_numero(numero_vuelo)
        if not vuelo:
            return None
        return self._vuelo_a_dto(vuelo)
        
    def actualizar_vuelo(self, vuelo_id: int, vuelo_dto: VueloDTO) -> Optional[VueloDTO]:
        """Actualiza un vuelo existente"""
        vuelo_data = vuelo_dto.dict(exclude_unset=True)
        vuelo_actualizado = self.repo.actualizar_vuelo(vuelo_id, vuelo_data)
        if not vuelo_actualizado:
            return None
        return self._vuelo_a_dto(vuelo_actualizado)
        
    def vuelo_esta_en_lista(self, vuelo_id: int) -> bool:
        """Verifica si un vuelo está actualmente en la lista doble"""
        return self.repo.vuelo_esta_en_lista(vuelo_id)
        
    def eliminar_vuelo(self, vuelo_id: int) -> bool:
        """Elimina un vuelo si no está en la lista doble"""
        # Verificar primero si el vuelo está en la lista
        if self.vuelo_esta_en_lista(vuelo_id):
            return False
        
        return self.repo.eliminar_vuelo(vuelo_id)
        
    def _vuelo_a_dto(self, vuelo: Vuelo) -> VueloDTO:
        """Convierte un modelo Vuelo a un DTO"""
        return VueloDTO(
            id=vuelo.id,
            numero_vuelo=vuelo.numero_vuelo,
            origen=vuelo.origen,
            destino=vuelo.destino,
            hora_salida=vuelo.hora_salida,
            hora_llegada=vuelo.hora_llegada,
            prioridad=vuelo.prioridad,
            estado=vuelo.estado,
            emergencia=vuelo.emergencia
        )
