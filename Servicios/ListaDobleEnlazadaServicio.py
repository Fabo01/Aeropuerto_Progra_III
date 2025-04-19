from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from Repositorios.ListaDobleEnlazadaCentinelasRepo import ListaDobleEnlazadaCentinelasRepo
from Repositorios.VueloRepo import VueloRepo
from Dominio.Modelos.NodoDobleVuelos import NodoDobleVuelos
from Dominio.Modelos.ListaDobleEnlCent import ListaDobleEnlazadaCentinelas
from Presentacion.DTOs.ListaDobleEnlazadaCentinelasDTO import ListaDobleEnlazadaCentinelasDTO, ListaConNodosDTO
from Presentacion.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO
from Presentacion.DTOs.VueloDTO import VueloDTO
from Servicios.VueloServicio import VueloServicio

class ListaDobleEnlazadaServicio:
    def __init__(self, db: Session):
        self.lista_repo = ListaDobleEnlazadaCentinelasRepo(db)
        self.vuelo_repo = VueloRepo(db)
        self.vuelo_servicio = VueloServicio(db)
        self.db = db
        
    def obtener_o_crear_lista_principal(self) -> ListaDobleEnlazadaCentinelasDTO:
        """Obtiene la lista principal o la crea si no existe"""
        lista = self.lista_repo.obtener_lista_por_nombre("principal")
        if not lista:
            lista = self.lista_repo.crear_lista("principal")
        return self._lista_a_dto(lista)
        
    def obtener_lista_por_id(self, lista_id: int) -> Optional[ListaDobleEnlazadaCentinelasDTO]:
        """Obtiene una lista por su ID"""
        lista = self.lista_repo.obtener_lista_por_id(lista_id)
        if not lista:
            return None
        return self._lista_a_dto(lista)
        
    def obtener_todas_listas(self) -> List[ListaDobleEnlazadaCentinelasDTO]:
        """Obtiene todas las listas"""
        listas = self.lista_repo.obtener_todas_listas()
        return [self._lista_a_dto(lista) for lista in listas]
        
    def obtener_lista_con_nodos(self) -> Optional[ListaConNodosDTO]:
        """Obtiene la lista principal con todos sus nodos"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Obtenemos los nodos de la lista
        nodos = self.lista_repo.obtener_nodos_de_lista(lista_dto.id)
        
        # Crear el DTO completo con los nodos
        lista_con_nodos = ListaConNodosDTO(
            id=lista_dto.id,
            nombre=lista_dto.nombre,
            tamanio=lista_dto.tamanio,
            cabezon_id=lista_dto.cabezon_id,
            colon_id=lista_dto.colon_id,
            nodos=[self._nodo_a_dto(nodo) for nodo in nodos]
        )
        
        return lista_con_nodos
        
    def insertar_vuelo_al_frente(self, vuelo_id: int) -> Optional[NodoDobleVueloDTO]:
        """Inserta un vuelo al principio de la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Insertamos el vuelo al frente
        nodo = self.lista_repo.insertar_nodo_al_frente(lista_dto.id, vuelo_id)
        if not nodo:
            return None
        return self._nodo_a_dto(nodo)
        
    def insertar_vuelo_al_final(self, vuelo_id: int) -> Optional[NodoDobleVueloDTO]:
        """Inserta un vuelo al final de la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Insertamos el vuelo al final
        nodo = self.lista_repo.insertar_nodo_al_final(lista_dto.id, vuelo_id)
        if not nodo:
            return None
        return self._nodo_a_dto(nodo)
        
    def extraer_vuelo_de_posicion(self, posicion: int) -> Optional[VueloDTO]:
        """Extrae un vuelo de una posición específica de la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Obtener todos los nodos
        nodos = self.lista_repo.obtener_nodos_de_lista(lista_dto.id)
        
        # Buscar el nodo en la posición indicada
        nodo_a_extraer = None
        for nodo in nodos:
            if nodo.posicion == posicion:
                nodo_a_extraer = nodo
                break
                
        if not nodo_a_extraer:
            return None
            
        # Extraer el nodo
        nodo_extraido, exito = self.lista_repo.extraer_nodo(nodo_a_extraer.id)
        if not exito or not nodo_extraido:
            return None
            
        # Obtener y devolver el vuelo
        vuelo = self.vuelo_repo.obtener_vuelo_por_id(nodo_extraido.vuelo_id)
        if not vuelo:
            return None
            
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
        
    def insertar_vuelo_ordenado_por_prioridad(self, vuelo_id: int) -> Optional[NodoDobleVueloDTO]:
        """
        Inserta un vuelo en la posición correcta según su prioridad y estado de emergencia.
        Los vuelos de emergencia van al frente de la lista principal.
        """
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        vuelo = self.vuelo_repo.obtener_vuelo_por_id(vuelo_id)
        if not vuelo:
            return None
            
        # Si es emergencia, insertar al frente
        if vuelo.emergencia:
            return self._nodo_a_dto(self.lista_repo.insertar_nodo_al_frente(lista_dto.id, vuelo_id))
            
        # Obtener todos los nodos para determinar la posición correcta
        nodos = self.lista_repo.obtener_nodos_de_lista(lista_dto.id)
        
        # Si no hay nodos o todos son de emergencia, insertar al final
        if not nodos:
            return self._nodo_a_dto(self.lista_repo.insertar_nodo_al_final(lista_dto.id, vuelo_id))
            
        # Determinar la posición correcta según la prioridad
        posicion_insercion = 0
        for nodo in nodos:
            nodo_vuelo = self.vuelo_repo.obtener_vuelo_por_id(nodo.vuelo_id)
            
            # Primero pasar todos los vuelos de emergencia
            if nodo_vuelo.emergencia:
                posicion_insercion += 1
                continue
                
            # Luego ordenar por prioridad (mayor primero)
            if not nodo_vuelo.emergencia and nodo_vuelo.prioridad > vuelo.prioridad:
                posicion_insercion += 1
                continue
                
            # Si tienen misma prioridad, ordenar por hora de salida
            if (not nodo_vuelo.emergencia and 
                nodo_vuelo.prioridad == vuelo.prioridad and 
                nodo_vuelo.hora_salida < vuelo.hora_salida):
                posicion_insercion += 1
                continue
                
            # Encontramos la posición correcta
            break
            
        # TODO: Implementar la inserción en una posición específica
        # Por ahora, insertamos al frente o al final según corresponda
        if posicion_insercion == 0:
            return self._nodo_a_dto(self.lista_repo.insertar_nodo_al_frente(lista_dto.id, vuelo_id))
        else:
            return self._nodo_a_dto(self.lista_repo.insertar_nodo_al_final(lista_dto.id, vuelo_id))
    
    def reordenar_lista_por_prioridad(self) -> bool:
        """Reordena todos los nodos de la lista principal según prioridad y estado de emergencia"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        return self.lista_repo.reordenar_lista_por_prioridad(lista_dto.id)

    def insertar_vuelo_en_posicion(self, vuelo_id: int, posicion: int) -> Optional[NodoDobleVueloDTO]:
        """
        Inserta un vuelo en una posición específica de la lista principal.
        Si la posición es negativa, inserta al frente.
        Si la posición es mayor que el tamaño de la lista, inserta al final.
        """
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Insertamos el vuelo en la posición especificada
        nodo = self.lista_repo.insertar_nodo_en_posicion(lista_dto.id, vuelo_id, posicion)
        if not nodo:
            return None
        return self._nodo_a_dto(nodo)

    def obtener_cantidad_nodos(self) -> int:
        """Obtiene la cantidad de nodos en la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        return lista_dto.tamanio

    def obtener_primer_vuelo(self) -> Optional[VueloDTO]:
        """Obtiene el primer vuelo de la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Obtener el primer nodo 
        primer_nodo = self.lista_repo.obtener_primer_nodo(lista_dto.id)
        if not primer_nodo:
            return None
            
        # Obtener el vuelo asociado al primer nodo
        vuelo = self.vuelo_repo.obtener_vuelo_por_id(primer_nodo.vuelo_id)
        if not vuelo:
            return None
            
        return self.vuelo_servicio._vuelo_a_dto(vuelo)

    def obtener_ultimo_vuelo(self) -> Optional[VueloDTO]:
        """Obtiene el último vuelo de la lista principal"""
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        # Obtener el último nodo 
        ultimo_nodo = self.lista_repo.obtener_ultimo_nodo(lista_dto.id)
        if not ultimo_nodo:
            return None
            
        # Obtener el vuelo asociado al último nodo
        vuelo = self.vuelo_repo.obtener_vuelo_por_id(ultimo_nodo.vuelo_id)
        if not vuelo:
            return None
            
        return self.vuelo_servicio._vuelo_a_dto(vuelo)

    def mover_nodo_entre_posiciones(self, posicion_origen: int, posicion_destino: int) -> bool:
        """
        Mueve un nodo de una posición a otra en la lista principal.
        
        Args:
            posicion_origen: Posición actual del nodo a mover
            posicion_destino: Posición a la que se moverá el nodo
            
        Returns:
            bool: True si el movimiento se realizó correctamente, False en caso contrario
        """
        # Obtenemos o creamos la lista principal
        lista_dto = self.obtener_o_crear_lista_principal()
        
        return self.lista_repo.mover_nodo_entre_posiciones(lista_dto.id, posicion_origen, posicion_destino)

    def _lista_a_dto(self, lista: ListaDobleEnlazadaCentinelas) -> ListaDobleEnlazadaCentinelasDTO:
        """Convierte un modelo Lista a un DTO"""
        return ListaDobleEnlazadaCentinelasDTO(
            id=lista.id,
            nombre=lista.nombre,
            tamanio=lista.tamanio,
            cabezon_id=lista.cabezon_id,
            colon_id=lista.colon_id
        )
        
    def _nodo_a_dto(self, nodo: NodoDobleVuelos) -> NodoDobleVueloDTO:
        """Convierte un modelo Nodo a un DTO"""
        vuelo = self.vuelo_repo.obtener_vuelo_por_id(nodo.vuelo_id)
        vuelo_dto = VueloDTO(
            id=vuelo.id,
            numero_vuelo=vuelo.numero_vuelo,
            origen=vuelo.origen,
            destino=vuelo.destino,
            hora_salida=vuelo.hora_salida,
            hora_llegada=vuelo.hora_llegada,
            prioridad=vuelo.prioridad,
            estado=vuelo.estado,
            emergencia=vuelo.emergencia
        ) if vuelo else None
        
        return NodoDobleVueloDTO(
            id=nodo.id,
            vuelo=vuelo_dto,
            posicion=nodo.posicion,
            lista_id=nodo.estado_header.id if nodo.estado_header else nodo.estado_trailer.id if nodo.estado_trailer else 0,
            anterior_id=nodo.anterior_id,
            siguiente_id=nodo.siguiente_id
        )
