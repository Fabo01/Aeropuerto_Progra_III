from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .Base import Base

class Vuelo(Base):
    __tablename__ = 'vuelos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_vuelo = Column(String, unique=True, nullable=False)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    hora_salida = Column(DateTime, nullable=False)
    hora_llegada = Column(DateTime, nullable=False)
    prioridad = Column(Integer, default=0)  # Prioridad del vuelo (0 por defecto) desde el 0 hasta el 100, siendo 100 la mayor prioridad
    estado = Column(Enum('programado', 'retrasado', 'cancelado'), default='programado')  # Estado del vuelo
    emergencia = Column(Boolean, default=False)  # Indica si el vuelo es una emergencia
    
    # Relación con la estructura de lista doblemente enlazada
    lista_item = relationship("NodoDobleVuelos", back_populates="vuelo", uselist=False)

    def __repr__(self):
        return f"<Vuelo {self.numero_vuelo} {self.origen}->{self.destino} {self.estado}>"
