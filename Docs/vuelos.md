# ✈️ Sistema de Gestión de Vuelos

## Descripción General

El módulo de gestión de vuelos es el componente central del sistema de control de aeropuerto. Permite la creación, actualización, seguimiento y priorización de vuelos en tiempo real.

## Entidad Vuelo

La entidad `Vuelo` representa toda la información necesaria para gestionar un vuelo en el aeropuerto, desde sus datos básicos hasta su estado operativo.

### Atributos Principales

| Atributo | Tipo | Descripción |
|----------|------|--ks-----------|
| `id` | Integer | Identificador único del vuelo |
| `numero_vuelo` | String | Código alfanumérico único (ej: IB2021) |
| `origen` | String | Aeropuerto de origen |
| `destino` | String | Aeropuerto de destino |
| `hora_salida` | DateTime | Fecha y hora programada de despegue |
| `hora_llegada` | DateTime | Fecha y hora estimada de llegada |
| `prioridad` | Integer | Nivel de prioridad (0-100) |
| `estado` | Enum | Estado actual del vuelo (programado, retrasado, cancelado) |
| `emergencia` | Boolean | Indica si el vuelo está en situación de emergencia |

### Modelo de Datos

```python
class Vuelo(Base):
    __tablename__ = 'vuelos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_vuelo = Column(String, unique=True, nullable=False)
    origen = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    hora_salida = Column(DateTime, nullable=False)
    hora_llegada = Column(DateTime, nullable=False)
    prioridad = Column(Integer, default=0)
    estado = Column(Enum('programado', 'retrasado', 'cancelado'), default='programado')
    emergencia = Column(Boolean, default=False)
    
    # Relación con la lista doblemente enlazada
    lista_item = relationship("NodoDobleVuelos", back_populates="vuelo", uselist=False)
    
    def __repr__(self):
        return f"<Vuelo {self.numero_vuelo} {self.origen}->{self.destino} {self.estado}>"
```

## DTOs (Data Transfer Objects)

### VueloDTO

Utilizado para transportar información de vuelos entre la API y los clientes.

```python
class VueloDTO(BaseModel):
    id: Optional[int]
    numero_vuelo: str
    origen: str
    destino: str
    hora_salida: datetime
    hora_llegada: datetime
    prioridad: Optional[int] = 0
    estado: Optional[str] = 'programado'
    emergencia: Optional[bool] = False

    class Config:
        from_attributes = True
```

### VueloCreadoDTO

Especializado para la creación de nuevos vuelos (sin ID).

```python
class VueloCreadoDTO(BaseModel):
    numero_vuelo: str
    origen: str
    destino: str
    hora_salida: datetime
    hora_llegada: datetime
    prioridad: Optional[int] = 0
    estado: Optional[str] = 'programado'
    emergencia: Optional[bool] = False

    class Config:
        from_attributes = True
```

## Servicio de Vuelos

El servicio `VueloServicio` implementa la lógica de negocio relacionada con la gestión de vuelos:

```python
class VueloServicio:
    def __init__(self, db: Session):
        self.repo = VueloRepo(db)
        
    def crear_vuelo(self, vuelo_dto: Union[VueloDTO, VueloCreadoDTO]) -> VueloDTO:
        # Implementación
        
    def obtener_vuelos(self) -> List[VueloDTO]:
        # Implementación
        
    def obtener_vuelo_por_id(self, vuelo_id: int) -> Optional[VueloDTO]:
        # Implementación
        
    def actualizar_vuelo(self, vuelo_id: int, vuelo_dto: VueloDTO) -> Optional[VueloDTO]:
        # Implementación
        
    def vuelo_esta_en_lista(self, vuelo_id: int) -> bool:
        # Implementación
        
    def eliminar_vuelo(self, vuelo_id: int) -> bool:
        # Implementación
```

## Sistema de Priorización

### Cálculo de Prioridad

La prioridad de un vuelo se determina por varios factores:

1. **Emergencia**: Los vuelos en emergencia tienen prioridad absoluta
2. **Prioridad manual**: Valor asignado manualmente (0-100)
3. **Estado**: Los vuelos programados tienen prioridad sobre los retrasados o cancelados
4. **Proximidad temporal**: Cuanto más cercana es la hora de salida, mayor prioridad

### Algoritmo de Priorización

```python
def calcular_prioridad_efectiva(vuelo):
    # Prioridad base: valor manual asignado (0-100)
    prioridad = vuelo.prioridad
    
    # Factor emergencia (prioridad máxima)
    if vuelo.emergencia:
        prioridad += 1000
    
    # Factor estado
    if vuelo.estado == 'programado':
        prioridad += 100
    elif vuelo.estado == 'retrasado':
        prioridad += 50
    # Los cancelados mantienen su prioridad base
    
    # Factor temporal (más próximo = más prioritario)
    tiempo_actual = datetime.now()
    minutos_para_salida = (vuelo.hora_salida - tiempo_actual).total_seconds() / 60
    
    # Ajuste por proximidad (0-200 puntos adicionales)
    # Más cercano = más puntos, con un máximo para vuelos dentro de 3 horas
    if minutos_para_salida <= 0:
        ajuste_temporal = 200  # Ya debería haber salido
    elif minutos_para_salida <= 180:  # Dentro de 3 horas
        ajuste_temporal = 200 - (minutos_para_salida / 180 * 200)
    else:
        ajuste_temporal = 0
    
    prioridad += ajuste_temporal
    
    return prioridad
```

## Flujos de Trabajo Principales

### 1. Creación de un Vuelo

1. Se reciben los datos del vuelo en formato `VueloCreadoDTO`
2. Se validan los datos (número de vuelo único, formato correcto, etc.)
3. Se crea el registro en la base de datos
4. Se genera y devuelve un `VueloDTO` con el ID asignado

### 2. Modificación de Estado

1. Se recibe la solicitud de cambio de estado para un vuelo específico
2. Se verifica si el vuelo existe y si el estado nuevo es válido
3. Se actualiza el estado en la base de datos
4. Si el vuelo está en la lista de vuelos, se reordena la lista según la nueva prioridad

### 3. Activación de Emergencia

1. Se recibe notificación de emergencia para un vuelo
2. Se actualiza el estado `emergencia` a `True`
3. Se reordena automáticamente la lista de vuelos para darle máxima prioridad
4. Se notifica al sistema la situación de emergencia

### 4. Completar un Vuelo

1. Se extrae el vuelo de la lista
2. Se registra como completado en el historial
3. Se notifica al sistema para actualizar estadísticas

## Validaciones

El sistema implementa las siguientes validaciones para garantizar la integridad de los datos:

```python
# Ejemplos de validaciones implementadas
def validar_numero_vuelo(numero_vuelo):
    # Formato: 2 letras seguidas de 3-4 dígitos
    pattern = r'^[A-Z]{2}\d{3,4}$'
    return re.match(pattern, numero_vuelo) is not None

def validar_fechas(hora_salida, hora_llegada):
    # La hora de llegada debe ser posterior a la de salida
    return hora_llegada > hora_salida

def validar_prioridad(prioridad):
    # La prioridad debe estar entre 0 y 100
    return 0 <= prioridad <= 100
```

## Interfaz de Usuario

La aplicación implementa múltiples vistas para la gestión de vuelos:

1. **Dashboard**: Vista general con indicadores y próximo vuelo
2. **Lista de Vuelos**: Tabla con todos los vuelos y sus detalles
3. **Detalle de Vuelo**: Formulario para crear y editar vuelos
4. **Gestión de Lista**: Interfaz para manipular la lista doblemente enlazada

### Elementos Visuales

- **Indicadores de Estado**: Código de colores para visualizar rápidamente el estado
  - Rojo: Emergencia
  - Amarillo: Retrasado
  - Gris: Cancelado
  - Verde: Programado

- **Formularios de Edición**: Validación en tiempo real de los datos ingresados
- **Confirmaciones**: Diálogos de confirmación para acciones críticas

## API REST

Los endpoints para la gestión de vuelos incluyen:

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /vuelos/ | Obtener todos los vuelos |
| POST | /vuelos/ | Crear un nuevo vuelo |
| GET | /vuelos/{id} | Obtener un vuelo específico |
| PUT | /vuelos/{id} | Actualizar un vuelo |
| DELETE | /vuelos/{id} | Eliminar un vuelo |
| PATCH | /vuelos/{id}/emergencia | Activar/desactivar emergencia |
| PATCH | /vuelos/{id}/estado | Cambiar estado |
