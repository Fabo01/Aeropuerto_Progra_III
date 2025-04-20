# 🔄 Lista Doblemente Enlazada con Centinelas

## Descripción General

La Lista Doblemente Enlazada con Centinelas es una estructura de datos fundamental en el sistema de gestión de vuelos del aeropuerto. Proporciona un mecanismo eficiente para organizar, priorizar y gestionar los vuelos.

## Características Principales

- **Enlaces bidireccionales**: Cada nodo mantiene referencias tanto al nodo anterior como al siguiente
- **Nodos centinela**: Nodos especiales (`cabezon` y `colon`) que marcan los extremos de la lista
- **Persistencia en base de datos**: Implementación que permite guardar el estado de la estructura en SQLite
- **Ordenamiento dinámico**: Capacidad para reordenar vuelos según prioridad y estado de emergencia

## Tipo de Dato Abstracto (TDA)

### Estructura Base

```python
class NodoDoble:
    __slots__ = '_elemento', '_anterior', '_siguiente'
    def __init__(self, elemento=None, anterior=None, siguiente=None):
        self._elemento = elemento
        self._anterior = anterior
        self._siguiente = siguiente

class ListaDoblementeEnlazadaCentinela:
    def __init__(self):
        self._cabezon = NodoDoble()  # Centinela de inicio
        self._colon = NodoDoble()    # Centinela de fin
        self._cabezon._siguiente = self._colon
        self._colon._anterior = self._cabezon
        self._tamanio = 0
```

### Operaciones Fundamentales

| Operación | Descripción | Complejidad |
|-----------|-------------|-------------|
| `esta_vacia()` | Comprueba si la lista está vacía | O(1) |
| `tamaño()` | Obtiene el número de elementos | O(1) |
| `primer_elemento()` | Obtiene el primer elemento (sin removerlo) | O(1) |
| `ultimo_elemento()` | Obtiene el último elemento (sin removerlo) | O(1) |
| `insertar_al_frente(elemento)` | Añade un elemento al inicio | O(1) |
| `insertar_al_final(elemento)` | Añade un elemento al final | O(1) |
| `insertar_en_posicion(elemento, pos)` | Añade un elemento en una posición específica | O(n) |
| `extraer_primero()` | Elimina y devuelve el primer elemento | O(1) |
| `extraer_ultimo()` | Elimina y devuelve el último elemento | O(1) |
| `extraer_de_posicion(pos)` | Elimina y devuelve el elemento en una posición específica | O(n) |
| `mover_nodo(origen, destino)` | Mueve un nodo de una posición a otra | O(n) |

## Implementación en el Sistema

La lista doblemente enlazada se implementa a través de tres modelos principales:

### 1. ListaDobleEnlazadaCentinelas

```python
class ListaDobleEnlazadaCentinelas(Base):
    __tablename__ = "ListaDobleEnlazadaCentinelas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False, default="principal")
    cabezon_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=False)
    colon_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=False)
    tamanio = Column(Integer, default=0)
    
    # Relaciones con los centinelas
    header = relationship("NodoDobleVuelos", foreign_keys=[cabezon_id], back_populates="estado_header")
    trailer = relationship("NodoDobleVuelos", foreign_keys=[colon_id], back_populates="estado_trailer")
```

### 2. NodoDobleVuelos

```python
class NodoDobleVuelos(Base):
    __tablename__ = "NodoDobleVuelos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    posicion = Column(Integer, nullable=True)
    
    # Enlaces de la lista doblemente enlazada
    anterior_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=True)
    siguiente_id = Column(Integer, ForeignKey('NodoDobleVuelos.id'), nullable=True)
    
    # Relación con el elemento contenido
    vuelo_id = Column(Integer, ForeignKey('vuelos.id'), nullable=True)
    vuelo = relationship("Vuelo", back_populates="lista_item")
    
    # Metadatos del nodo
    centinela = Column(Enum("cabezon", "colon"), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    creado_en = Column(DateTime, default=datetime.now, nullable=False)
```

### 3. Vuelo

```python
class Vuelo(Base):
    # ...otros campos...
    
    # Relación con la estructura de lista
    lista_item = relationship("NodoDobleVuelos", back_populates="vuelo", uselist=False)
```

## Diagrama Conceptual

```
+----------------+      +----------------+      +----------------+      +----------------+
|   CENTINELA    |      |     NODO 1     |      |     NODO 2     |      |   CENTINELA    |
|   (cabezon)    |<---->|  (vuelo_id=5)  |<---->|  (vuelo_id=8)  |<---->|    (colon)     |
+----------------+      +----------------+      +----------------+      +----------------+
```

## Ventajas de esta Implementación

1. **Eliminación de casos borde**: Los nodos centinela eliminan la necesidad de casos especiales para el primer y último elemento.
2. **Eficiencia en operaciones**: Las operaciones en los extremos son O(1).
3. **Navegación bidireccional**: Permite recorrer la estructura en ambas direcciones.
4. **Persistencia**: El estado completo de la estructura se almacena en la base de datos.
5. **Control de versiones**: El campo `version` permite mantener un historial de cambios en la estructura.

## Ejemplo de Uso

### Insertar un vuelo al inicio de la lista

```python
def insertar_vuelo_al_inicio(lista_id: int, vuelo_id: int):
    servicio = ListaDobleEnlazadaServicio(db)
    servicio.insertar_al_frente(lista_id, vuelo_id)
```

### Extraer el primer vuelo

```python
def extraer_primer_vuelo(lista_id: int):
    servicio = ListaDobleEnlazadaServicio(db)
    nodo = servicio.extraer_primero(lista_id)
    if nodo and nodo.vuelo:
        return nodo.vuelo
    return None
```

### Reordenar la lista por prioridad

```python
def reordenar_por_prioridad(lista_id: int):
    servicio = ListaDobleEnlazadaServicio(db)
    servicio.reordenar_por_prioridad(lista_id)
```

## Algoritmos Clave

### Reordenamiento por Prioridad

El sistema implementa un algoritmo de ordenamiento por inserción adaptado para la lista doblemente enlazada, que tiene en cuenta:

1. Vuelos en estado de emergencia (prioridad máxima)
2. Nivel de prioridad del vuelo (0-100)
3. Estado del vuelo (programado, retrasado o cancelado)
4. Horario de salida (vuelos próximos a salir tienen mayor prioridad)

```python
# Pseudocódigo simplificado
def reordenar_por_prioridad(lista):
    # Crear lista temporal ordenada
    vuelos_ordenados = []
    nodo_actual = lista.primer_nodo()
    
    # Recorrer la lista original
    while nodo_actual != None:
        vuelo = nodo_actual.vuelo
        posicion = calcular_posicion_ideal(vuelo, vuelos_ordenados)
        insertar_en_posicion(vuelos_ordenados, vuelo, posicion)
        nodo_actual = nodo_actual.siguiente
    
    # Reconstruir la lista original con el nuevo orden
    reconstruir_lista(lista, vuelos_ordenados)
```
