from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .Base import Base

class ListaDobleEnlazadaCentinelas(Base):
    """
    Representa el estado de una lista doblemente enlazada en la base de datos.
    Mantiene referencias a los nodos centinela y el tamaño de la lista.
    """
    __tablename__ = "ListaDobleEnlazadaCentinelas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False, default="principal")  # Nombre identificador de la lista
    
    # Referencias a los nodos centinela
    cabezon_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=False)
    colon_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=False)
    
    # Relaciones con los centinelas
    header = relationship("NodoDobleVuelos", foreign_keys=[cabezon_id], back_populates="estado_header")   # Cabezon
    trailer = relationship("NodoDobleVuelos", foreign_keys=[colon_id], back_populates="estado_trailer") # Colon
    
    # Tamaño de la lista (excluyendo centinelas)
    tamanio = Column(Integer, default=0)

    def __repr__(self):
        return f"<ListaDobleEnlazadaCentinelas nombre={self.nombre} tamanio={self.tamanio}>"