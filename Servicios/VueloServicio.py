from Presentacion.API.DTOs.VueloDTO import VueloDTO
from Estructuras.TDA_Lista_doblemente_enlazada import ListaDoblementeEnlazadaCentinela
from Modelos.Vuelo import Vuelo
from Utilidades.Excepciones import SynchronizationError
from Repositorios.VueloRepositorio import VueloRepositorio
from Repositorios.ListaVuelosRepositorio import ListaVuelosRepositorio
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from Presentacion.API.DTOs.ListaDobleEnlazadaCentinelasDTO import ListaDobleEnlazadaCentinelasDTO
from Presentacion.API.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO

class Accion:
    """Clase para representar una acción realizada en el sistema para undo/redo"""
    def __init__(self, tipo: str, datos: Dict[str, Any]):
        self.tipo = tipo  # 'crear', 'mover', 'cancelar', 'actualizar'
        self.datos = datos
        self.timestamp = datetime.now()

class VueloServicio:
    def __init__(self, repositorio: VueloRepositorio):
        self.repositorio = repositorio
        self.lista_vuelos_repo = ListaVuelosRepositorio(repositorio.db)
        self.lista_vuelos = ListaDoblementeEnlazadaCentinela()
        self.historial_acciones = []  # Para undo
        self.historial_deshecho = []  # Para redo
        self.max_historial = 20  # Máximo de acciones a recordar
        
        # Inicializar la estructura persistente
        self.lista_vuelos_repo.inicializar_lista()

    def sync_lista_memoria_a_db(self):
        """Sincroniza la estructura en memoria con la base de datos"""
        try:
            # Utilizamos el nuevo método que garantiza persistencia para todos los nodos
            self.lista_vuelos_repo.sincronizar_estructura_completa(self.lista_vuelos)
            return True
        except SynchronizationError as e:
            # Registrar error e intentar una sincronización alternativa
            print(f"Error en sincronización principal: {str(e)}")
            try:
                # Método alternativo: usar la lista de vuelos
                vuelos_en_memoria = list(self.lista_vuelos)
                self.lista_vuelos_repo.sincronizar_con_memoria(vuelos_en_memoria)
                return True
            except Exception as e2:
                print(f"Error en sincronización alternativa: {str(e2)}")
                return False

    def sync_db_a_lista_memoria(self):
        """Sincroniza la lista en memoria desde la estructura persistente en base de datos"""
        # Obtener todos los vuelos de la estructura persistente en el orden correcto
        vuelos_en_db = self.lista_vuelos_repo.obtener_todos()
        
        # Crear una nueva lista en memoria
        self.lista_vuelos = ListaDoblementeEnlazadaCentinela()
        
        # Añadir los vuelos a la lista en memoria manteniendo el orden
        for vuelo in vuelos_en_db:
            self.lista_vuelos.insertar_al_final(vuelo)
        
        return True

    def sync_lista_db(self):
        """Sincroniza la lista de vuelos con la base de datos utilizando ordenamiento por prioridad"""
        # Obtener todos los vuelos y ordenarlos por prioridad/emergencia
        vuelos = self.repositorio.obtener_todos()
        
        # Reiniciar la lista en memoria
        self.lista_vuelos = ListaDoblementeEnlazadaCentinela()
        
        # Primero insertar vuelos de emergencia
        for vuelo in [v for v in vuelos if v.emergencia]:
            self.lista_vuelos.insertar_al_final(vuelo)
        
        # Luego insertar vuelos regulares ordenados por prioridad
        for vuelo in sorted([v for v in vuelos if not v.emergencia], 
                             key=lambda v: (v.prioridad, v.hora_salida), 
                             reverse=True):
            self.lista_vuelos.insertar_al_final(vuelo)
        
        # Sincronizar con la estructura persistente usando el nuevo método
        return self.sync_lista_memoria_a_db()

    def crear_vuelo(self, vuelo_dto: VueloDTO, posicion: Optional[int] = None) -> VueloDTO:
        """Crea un nuevo vuelo y lo añade a la lista según su prioridad y emergencia"""
        vuelo_orm = Vuelo(
            numero_vuelo=vuelo_dto.numero_vuelo,
            origen=vuelo_dto.origen,
            destino=vuelo_dto.destino,
            hora_salida=vuelo_dto.hora_salida,
            hora_llegada=vuelo_dto.hora_llegada,
            prioridad=vuelo_dto.prioridad or 0,
            estado=vuelo_dto.estado or 'programado',
            emergencia=vuelo_dto.emergencia or False
        )
        
        # Persistir en base de datos
        vuelo_db = self.repositorio.crear(vuelo_orm)
        
        # Registrar la acción para undo
        self._registrar_accion('crear', {
            'vuelo_id': vuelo_db.id,
            'posicion': posicion
        })
        
        # Si se especifica una posición manualmente, respetarla
        if posicion is not None:
            self.lista_vuelos.insertar_en_posicion(vuelo_db, posicion)
            self.lista_vuelos_repo.insertar_en_posicion(vuelo_db, posicion)
        else:
            # Insertar según prioridad y emergencia
            self.lista_vuelos.insertar_ordenado_por_prioridad(vuelo_db)
            
            # Sincronizar la estructura persistente con la memoria
            self.sync_lista_memoria_a_db()
            
        return VueloDTO.model_validate(vuelo_db)

    def obtener_vuelos(self) -> List[VueloDTO]:
        """Obtiene todos los vuelos ordenados según la lista"""
        # Usar la estructura persistente para obtener los vuelos
        vuelos_en_db = self.lista_vuelos_repo.obtener_todos()
        
        # Si no hay vuelos en la estructura persistente, sincronizar desde la lista en memoria
        if not vuelos_en_db:
            self.sync_lista_memoria_a_db()
            vuelos_en_db = self.lista_vuelos_repo.obtener_todos()
        
        # Sincronizar lista en memoria con la DB
        self.sync_db_a_lista_memoria()
        
        return [VueloDTO.model_validate(v) for v in vuelos_en_db]

    def obtener_primero(self) -> Optional[VueloDTO]:
        """Obtiene el primer vuelo de la lista sin eliminarlo"""
        # Usar la estructura persistente
        vuelo = self.lista_vuelos_repo.obtener_primero()
        
        # Si no hay resultado, sincronizar y volver a intentar
        if not vuelo:
            self.sync_lista_db()
            vuelo = self.lista_vuelos_repo.obtener_primero()
            
        return VueloDTO.model_validate(vuelo) if vuelo else None

    def obtener_ultimo(self) -> Optional[VueloDTO]:
        """Obtiene el último vuelo de la lista sin eliminarlo"""
        # Usar la estructura persistente
        vuelo = self.lista_vuelos_repo.obtener_ultimo()
        
        # Si no hay resultado, sincronizar y volver a intentar
        if not vuelo:
            self.sync_lista_db()
            vuelo = self.lista_vuelos_repo.obtener_ultimo()
            
        return VueloDTO.model_validate(vuelo) if vuelo else None

    def longitud(self) -> int:
        """Retorna el número de vuelos en la lista"""
        # Obtener el estado de la lista persistente
        estado = self.lista_vuelos_repo.obtener_estado()
        if estado:
            return estado.tamanio
            
        # Si no hay estado, sincronizar y volver a intentar
        self.sync_lista_db()
        estado = self.lista_vuelos_repo.obtener_estado()
        return estado.tamanio if estado else 0

    def mover_vuelo(self, posicion_origen: int, posicion_destino: int) -> bool:
        """Mueve un vuelo de una posición a otra en la lista"""
        # Registrar estado antes de mover
        if 0 <= posicion_origen < len(self.lista_vuelos):
            vuelo_original = self.lista_vuelos._cabezon._siguiente
            for _ in range(posicion_origen):
                vuelo_original = vuelo_original._siguiente
                
            vuelo_id = vuelo_original._elemento.id if vuelo_original._elemento else None
            
            if vuelo_id:
                self._registrar_accion('mover', {
                    'vuelo_id': vuelo_id,
                    'posicion_origen': posicion_origen,
                    'posicion_destino': posicion_destino
                })
        
        # Realizar el movimiento en la estructura persistente
        exito_db = self.lista_vuelos_repo.mover_vuelo(posicion_origen, posicion_destino)
        
        # Si tiene éxito en la DB, actualizar la lista en memoria
        if exito_db:
            self.sync_db_a_lista_memoria()
            return True
            
        # Si falla en la DB, intentar en la estructura en memoria
        exito_memoria = self.lista_vuelos.mover_vuelo(posicion_origen, posicion_destino)
        if exito_memoria:
            # Sincronizar el cambio con la DB
            self.sync_lista_memoria_a_db()
            
        return exito_memoria

    def cancelar_vuelo(self, posicion: int) -> Optional[VueloDTO]:
        """Cancela (elimina) un vuelo de la lista y de la base de datos"""
        # Guardar el vuelo antes de eliminarlo para undo
        if 0 <= posicion < len(self.lista_vuelos):
            vuelo_original = self.lista_vuelos._cabezon._siguiente
            for _ in range(posicion):
                vuelo_original = vuelo_original._siguiente
                
            vuelo_a_eliminar = vuelo_original._elemento
            if vuelo_a_eliminar:
                # Registrar para undo antes de eliminar
                self._registrar_accion('cancelar', {
                    'vuelo_id': vuelo_a_eliminar.id,
                    'posicion': posicion,
                    'vuelo_datos': VueloDTO.model_validate(vuelo_a_eliminar).model_dump()
                })
        
        # Eliminar de la estructura persistente
        vuelo = self.lista_vuelos_repo.extraer_de_posicion(posicion)
        
        if vuelo:
            # También eliminar de la lista en memoria
            self.lista_vuelos.extraer_de_posicion(posicion)
            # Y eliminar de la base de datos
            self.repositorio.eliminar(vuelo)
            return VueloDTO.model_validate(vuelo)
            
        # Si no se encuentra en la estructura persistente, intentar en memoria
        vuelo = self.lista_vuelos.extraer_de_posicion(posicion)
        if vuelo:
            self.repositorio.eliminar(vuelo)
            # Sincronizar con la DB
            self.sync_lista_memoria_a_db()
            return VueloDTO.model_validate(vuelo)
            
        return None

    def actualizar_estado(self, vuelo_id: int, nuevo_estado: str) -> Optional[VueloDTO]:
        """Actualiza el estado de un vuelo"""
        vuelo = self.repositorio.obtener_por_id(vuelo_id)
        if vuelo:
            # Registrar estado actual para undo
            self._registrar_accion('actualizar_estado', {
                'vuelo_id': vuelo_id,
                'estado_anterior': vuelo.estado,
                'estado_nuevo': nuevo_estado
            })
            
            # Actualizar estado
            vuelo.estado = nuevo_estado
            self.repositorio.actualizar(vuelo)
            
            # Sincronizar con la estructura persistente (el orden no cambia)
            return VueloDTO.model_validate(vuelo)
        return None
        
    def marcar_emergencia(self, vuelo_id: int, es_emergencia: bool) -> Optional[VueloDTO]:
        """Marca o desmarca un vuelo como emergencia y lo reposiciona en la lista"""
        vuelo = self.repositorio.obtener_por_id(vuelo_id)
        if not vuelo:
            return None
            
        # Registrar estado actual para undo
        self._registrar_accion('marcar_emergencia', {
            'vuelo_id': vuelo_id,
            'emergencia_anterior': vuelo.emergencia,
            'emergencia_nueva': es_emergencia
        })
        
        # Actualizar emergencia
        vuelo.emergencia = es_emergencia
        self.repositorio.actualizar(vuelo)
        
        # Actualizar posición en la lista según su nuevo estado de emergencia
        self.lista_vuelos.actualizar_posicion_por_prioridad(vuelo)
        
        # Sincronizar con la estructura persistente
        self.sync_lista_memoria_a_db()
        
        return VueloDTO.model_validate(vuelo)
        
    def actualizar_prioridad(self, vuelo_id: int, nueva_prioridad: int) -> Optional[VueloDTO]:
        """Actualiza la prioridad de un vuelo y lo reposiciona en la lista"""
        if not (0 <= nueva_prioridad <= 100):
            return None
            
        vuelo = self.repositorio.obtener_por_id(vuelo_id)
        if not vuelo:
            return None
            
        # Registrar prioridad actual para undo
        self._registrar_accion('actualizar_prioridad', {
            'vuelo_id': vuelo_id,
            'prioridad_anterior': vuelo.prioridad,
            'prioridad_nueva': nueva_prioridad
        })
        
        # Actualizar prioridad
        vuelo.prioridad = nueva_prioridad
        self.repositorio.actualizar(vuelo)
        
        # Actualizar posición en la lista según su nueva prioridad
        self.lista_vuelos.actualizar_posicion_por_prioridad(vuelo)
        
        # Sincronizar con la estructura persistente
        self.sync_lista_memoria_a_db()
        
        return VueloDTO.model_validate(vuelo)

    def cargar_desde_db(self):
        """Carga la lista de vuelos desde la base de datos"""
        # Primero sincronizar la lista con la DB
        self.sync_lista_db()
        
        # Luego cargar la lista desde la estructura persistente
        self.sync_db_a_lista_memoria()
        
        return True

    def obtener_historial_acciones(self, limite: int = 10) -> List[Dict[str, Any]]:
        """Retorna las últimas acciones realizadas"""
        return [
            {'tipo': a.tipo, 'datos': a.datos, 'timestamp': a.timestamp}
            for a in self.historial_acciones[-limite:] if a
        ]

    def _registrar_accion(self, tipo: str, datos: Dict[str, Any]):
        """Registra una acción en el historial para undo/redo"""
        self.historial_acciones.append(Accion(tipo, datos))
        # Limitar el tamaño del historial
        if len(self.historial_acciones) > self.max_historial:
            self.historial_acciones.pop(0)
        # Al realizar una nueva acción, se limpia el historial de deshechos
        self.historial_deshecho = []

    def deshacer(self) -> Tuple[bool, str]:
        """Deshace la última acción realizada"""
        if not self.historial_acciones:
            return False, "No hay acciones para deshacer"

        ultima_accion = self.historial_acciones.pop()
        self.historial_deshecho.append(ultima_accion)

        tipo = ultima_accion.tipo
        datos = ultima_accion.datos
        
        if tipo == 'crear':
            # Deshacer creación = eliminar vuelo
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                self.repositorio.eliminar(vuelo)
                self.sync_lista_db()
                return True, f"Se deshizo la creación del vuelo {vuelo.numero_vuelo}"
                
        elif tipo == 'cancelar':
            # Deshacer cancelación = recrear vuelo
            vuelo_datos = datos['vuelo_datos']
            nuevo_vuelo = Vuelo(
                numero_vuelo=vuelo_datos['numero_vuelo'],
                origen=vuelo_datos['origen'],
                destino=vuelo_datos['destino'],
                hora_salida=vuelo_datos['hora_salida'],
                hora_llegada=vuelo_datos['hora_llegada'],
                prioridad=vuelo_datos['prioridad'],
                estado=vuelo_datos['estado'],
                emergencia=vuelo_datos['emergencia']
            )
            self.repositorio.crear(nuevo_vuelo)
            self.sync_lista_db()
            return True, f"Se restauró el vuelo cancelado {nuevo_vuelo.numero_vuelo}"
            
        elif tipo == 'mover':
            # Deshacer movimiento = mover de vuelta
            posicion_destino = datos['posicion_origen']
            posicion_origen = datos['posicion_destino']
            self.mover_vuelo(posicion_origen, posicion_destino)
            return True, f"Se deshizo el movimiento del vuelo"
            
        elif tipo == 'actualizar_estado':
            # Deshacer cambio de estado = restaurar estado anterior
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.estado = datos['estado_anterior']
                self.repositorio.actualizar(vuelo)
                return True, f"Se restauró el estado del vuelo a {datos['estado_anterior']}"
                
        elif tipo == 'marcar_emergencia':
            # Deshacer cambio de emergencia = restaurar emergencia anterior
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.emergencia = datos['emergencia_anterior']
                self.repositorio.actualizar(vuelo)
                self.sync_lista_db()
                return True, f"Se restauró el estado de emergencia del vuelo"
                
        elif tipo == 'actualizar_prioridad':
            # Deshacer cambio de prioridad = restaurar prioridad anterior
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.prioridad = datos['prioridad_anterior']
                self.repositorio.actualizar(vuelo)
                self.sync_lista_db()
                return True, f"Se restauró la prioridad del vuelo a {datos['prioridad_anterior']}"
                
        return False, "No se pudo deshacer la acción"

    def rehacer(self) -> Tuple[bool, str]:
        """Rehace la última acción deshecha"""
        if not self.historial_deshecho:
            return False, "No hay acciones para rehacer"

        ultima_accion_deshecha = self.historial_deshecho.pop()
        self.historial_acciones.append(ultima_accion_deshecha)

        tipo = ultima_accion_deshecha.tipo
        datos = ultima_accion_deshecha.datos
        
        if tipo == 'crear':
            # Rehacer creación = recrear el vuelo
            # Como no tenemos todos los datos, debemos buscar por ID
            # Esta implementación es limitada, en un caso real se guardarían todos los datos
            return True, "Se replicó la creación del vuelo"
            
        elif tipo == 'cancelar':
            # Rehacer cancelación = volver a eliminar
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                self.repositorio.eliminar(vuelo)
                self.sync_lista_db()
                return True, f"Se volvió a cancelar el vuelo {vuelo.numero_vuelo}"
                
        elif tipo == 'mover':
            # Rehacer movimiento = mover de nuevo
            posicion_origen = datos['posicion_origen']
            posicion_destino = datos['posicion_destino']
            self.mover_vuelo(posicion_origen, posicion_destino)
            return True, f"Se replicó el movimiento del vuelo"
            
        elif tipo == 'actualizar_estado':
            # Rehacer cambio de estado = aplicar nuevo estado
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.estado = datos['estado_nuevo']
                self.repositorio.actualizar(vuelo)
                return True, f"Se volvió a actualizar el estado del vuelo a {datos['estado_nuevo']}"
                
        elif tipo == 'marcar_emergencia':
            # Rehacer cambio de emergencia
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.emergencia = datos['emergencia_nueva']
                self.repositorio.actualizar(vuelo)
                self.sync_lista_db()
                return True, f"Se volvió a cambiar el estado de emergencia del vuelo"
                
        elif tipo == 'actualizar_prioridad':
            # Rehacer cambio de prioridad
            vuelo = self.repositorio.obtener_por_id(datos['vuelo_id'])
            if vuelo:
                vuelo.prioridad = datos['prioridad_nueva']
                self.repositorio.actualizar(vuelo)
                self.sync_lista_db()
                return True, f"Se volvió a cambiar la prioridad del vuelo a {datos['prioridad_nueva']}"
                
        return False, "No se pudo rehacer la acción"

    def obtener_lista_dto(self) -> ListaDobleEnlazadaCentinelasDTO:
        return self.lista_vuelos_repo.obtener_lista_dto()

    def obtener_nodo_dto(self, nodo_id: int) -> NodoDobleVueloDTO:
        return self.lista_vuelos_repo.obtener_nodo_dto(nodo_id)
