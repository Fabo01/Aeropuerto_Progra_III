from sqlalchemy.orm import Session
from typing import List, Optional
from Dominio.Modelos.Vuelo import Vuelo
from sqlalchemy.exc import SQLAlchemyError

class VueloRepo:
    def __init__(self, db: Session):
        self.db = db
        
    def crear_vuelo(self, vuelo: Vuelo) -> Vuelo:
        try:
            self.db.add(vuelo)
            self.db.commit()
            self.db.refresh(vuelo)
            return vuelo
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
            
    def obtener_vuelos(self) -> List[Vuelo]:
        return self.db.query(Vuelo).all()
        
    def obtener_vuelo_por_id(self, vuelo_id: int) -> Optional[Vuelo]:
        return self.db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        
    def obtener_vuelo_por_numero(self, numero_vuelo: str) -> Optional[Vuelo]:
        return self.db.query(Vuelo).filter(Vuelo.numero_vuelo == numero_vuelo).first()
        
    def actualizar_vuelo(self, vuelo_id: int, vuelo_data: dict) -> Optional[Vuelo]:
        vuelo = self.obtener_vuelo_por_id(vuelo_id)
        if not vuelo:
            return None
            
        for key, value in vuelo_data.items():
            setattr(vuelo, key, value)
            
        try:
            self.db.commit()
            self.db.refresh(vuelo)
            return vuelo
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
            
    def vuelo_esta_en_lista(self, vuelo_id: int) -> bool:
        """Verifica si un vuelo está asociado a un nodo en la lista doble"""
        vuelo = self.obtener_vuelo_por_id(vuelo_id)
        if not vuelo:
            return False
        
        # Si el vuelo tiene un nodo asociado, está en la lista
        return vuelo.lista_item is not None

    def eliminar_vuelo(self, vuelo_id: int) -> bool:
        """Elimina un vuelo si no está en la lista doble"""
        vuelo = self.obtener_vuelo_por_id(vuelo_id)
        if not vuelo:
            return False
            
        # Verificar si el vuelo está en la lista
        if self.vuelo_esta_en_lista(vuelo_id):
            # No permitir eliminar vuelos que están en la lista
            return False
            
        try:
            self.db.delete(vuelo)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
