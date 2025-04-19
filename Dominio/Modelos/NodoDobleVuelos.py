from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .Base import Base

class NodoDobleVuelos(Base):
    """
    Representa un nodo en la lista doblemente enlazada persistente.
    Puede ser un nodo regular (con un vuelo asociado) o un nodo centinela (cabezon/colon).
    """
    __tablename__ = "NodoDobleVuelos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    posicion = Column(Integer, nullable=True)  # Posición en la lista (nulos para centinelas)
    
    # Relaciones con otros nodos
    anterior_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=True)
    siguiente_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=True)
    
    # Relación con vuelo (nula para centinelas)
    vuelo_id = Column(Integer, ForeignKey('vuelos.id'), nullable=True)
    vuelo = relationship("Vuelo", back_populates="lista_item")
    
    # Campo único para indicar si es un centinela y de qué tipo
    # NULL para nodos regulares, "cabezon" para header, "colon" para trailer
    centinela = Column(Enum("cabezon", "colon"), nullable=True)
    
    # Timestamp para tracking de creación del nodo
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
    
    # Indica si el nodo está activo en la lista actual (True) o es histórico (False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Versión de la estructura (incrementa con cada cambio estructural)
    version = Column(Integer, default=1, nullable=False)
    
    # Para el sistema de estados
    estado_header = relationship("ListaDobleEnlazadaCentinelas", foreign_keys="ListaDobleEnlazadaCentinelas.cabezon_id", back_populates="header", uselist=False)
    estado_trailer = relationship("ListaDobleEnlazadaCentinelas", foreign_keys="ListaDobleEnlazadaCentinelas.colon_id", back_populates="trailer", uselist=False)

    def __repr__(self):
        activo_str = "activo" if self.activo else "histórico"
        if self.centinela:
            return f"<Centinela {self.centinela} id={self.id} {activo_str}>"
        return f"<NodoDobleVuelos id={self.id} pos={self.posicion} vuelo_id={self.vuelo_id} {activo_str}>"

