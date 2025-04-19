from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from Dominio.Modelos.Vuelo import Vuelo
from Dominio.Modelos.ListaDobleEnlCent import ListaDobleEnlazadaCentinelas
from Dominio.Modelos.NodoDobleVuelos import NodoDobleVuelos
from datetime import datetime

class ListaDobleEnlazadaCentinelasRepo:
    def __init__(self, db: Session):
        self.db = db
        
    def crear_lista(self, nombre: str = "principal") -> Optional[ListaDobleEnlazadaCentinelas]:
        """Crea una nueva lista con sus nodos centinela"""
        try:
            # Crear los nodos centinela
            cabezon = NodoDobleVuelos(
                centinela="cabezon",
                creado_en=datetime.now(),
                activo=True
            )
            
            colon = NodoDobleVuelos(
                centinela="colon",
                creado_en=datetime.now(),
                activo=True
            )
            
            self.db.add(cabezon)
            self.db.add(colon)
            self.db.flush()  # Para obtener los IDs asignados
            
            # Enlazar los nodos centinela entre sí
            cabezon.siguiente_id = colon.id
            colon.anterior_id = cabezon.id
            
            # Crear la lista con los centinelas
            lista = ListaDobleEnlazadaCentinelas(
                nombre=nombre,
                cabezon_id=cabezon.id,
                colon_id=colon.id,
                tamanio=0
            )
            
            self.db.add(lista)
            self.db.commit()
            self.db.refresh(lista)
            return lista
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def obtener_lista_por_id(self, lista_id: int) -> Optional[ListaDobleEnlazadaCentinelas]:
        """Obtiene una lista por su ID"""
        return self.db.query(ListaDobleEnlazadaCentinelas).filter(
            ListaDobleEnlazadaCentinelas.id == lista_id
        ).first()
    
    def obtener_lista_por_nombre(self, nombre: str) -> Optional[ListaDobleEnlazadaCentinelas]:
        """Obtiene una lista por su nombre"""
        return self.db.query(ListaDobleEnlazadaCentinelas).filter(
            ListaDobleEnlazadaCentinelas.nombre == nombre
        ).first()
    
    def obtener_todas_listas(self) -> List[ListaDobleEnlazadaCentinelas]:
        """Obtiene todas las listas"""
        return self.db.query(ListaDobleEnlazadaCentinelas).all()
    
    def obtener_nodos_de_lista(self, lista_id: int) -> List[NodoDobleVuelos]:
        """Obtiene todos los nodos de una lista, ordenados por posición"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return []
            
        # Obtener el primer nodo (después del cabezon)
        primer_nodo = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.id == lista.header.siguiente_id,
            NodoDobleVuelos.activo == True
        ).first()
        
        if not primer_nodo:
            return []
            
        # Recorrer la lista y obtener todos los nodos
        nodos = []
        nodo_actual = primer_nodo
        
        while nodo_actual and nodo_actual.id != lista.colon_id:
            nodos.append(nodo_actual)
            nodo_actual = self.db.query(NodoDobleVuelos).filter(
                NodoDobleVuelos.id == nodo_actual.siguiente_id,
                NodoDobleVuelos.activo == True
            ).first()
            
        return nodos
        
    def insertar_nodo_al_frente(self, lista_id: int, vuelo_id: int) -> Optional[NodoDobleVuelos]:
        """Inserta un nuevo nodo al principio de la lista (después del cabezon)"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return None
            
        try:
            # Obtener los nodos centinela
            cabezon = self.db.query(NodoDobleVuelos).get(lista.cabezon_id)
            siguiente_actual = self.db.query(NodoDobleVuelos).get(cabezon.siguiente_id)
            
            # Crear el nuevo nodo
            nuevo_nodo = NodoDobleVuelos(
                vuelo_id=vuelo_id,
                anterior_id=cabezon.id,
                siguiente_id=siguiente_actual.id,
                posicion=0,
                creado_en=datetime.now(),
                activo=True
            )
            
            self.db.add(nuevo_nodo)
            self.db.flush()  # Para obtener el ID asignado
            
            # Actualizar los enlaces
            cabezon.siguiente_id = nuevo_nodo.id
            siguiente_actual.anterior_id = nuevo_nodo.id
            
            # Actualizar posiciones de los nodos siguientes
            self._actualizar_posiciones_siguientes(siguiente_actual.id)
            
            # Incrementar el tamaño de la lista
            lista.tamanio += 1
            
            self.db.commit()
            self.db.refresh(nuevo_nodo)
            return nuevo_nodo
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def insertar_nodo_al_final(self, lista_id: int, vuelo_id: int) -> Optional[NodoDobleVuelos]:
        """Inserta un nuevo nodo al final de la lista (antes del colon)"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return None
            
        try:
            # Obtener los nodos centinela
            colon = self.db.query(NodoDobleVuelos).get(lista.colon_id)
            anterior_actual = self.db.query(NodoDobleVuelos).get(colon.anterior_id)
            
            # Crear el nuevo nodo
            nuevo_nodo = NodoDobleVuelos(
                vuelo_id=vuelo_id,
                anterior_id=anterior_actual.id,
                siguiente_id=colon.id,
                posicion=lista.tamanio,  # La posición es el tamaño actual
                creado_en=datetime.now(),
                activo=True
            )
            
            self.db.add(nuevo_nodo)
            self.db.flush()  # Para obtener el ID asignado
            
            # Actualizar los enlaces
            anterior_actual.siguiente_id = nuevo_nodo.id
            colon.anterior_id = nuevo_nodo.id
            
            # Incrementar el tamaño de la lista
            lista.tamanio += 1
            
            self.db.commit()
            self.db.refresh(nuevo_nodo)
            return nuevo_nodo
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def insertar_nodo_en_posicion(self, lista_id: int, vuelo_id: int, posicion: int) -> Optional[NodoDobleVuelos]:
        """Inserta un nuevo nodo en una posición específica de la lista"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return None
            
        # Si la posición es negativa, insertar al frente
        if posicion <= 0:
            return self.insertar_nodo_al_frente(lista_id, vuelo_id)
            
        # Si la posición es mayor que el tamaño, insertar al final
        if posicion >= lista.tamanio:
            return self.insertar_nodo_al_final(lista_id, vuelo_id)
            
        try:
            # Obtener los nodos de la lista
            nodos = self.obtener_nodos_de_lista(lista_id)
            if not nodos:
                return self.insertar_nodo_al_final(lista_id, vuelo_id)
                
            # Encontrar el nodo en la posición donde queremos insertar
            nodo_en_posicion = None
            for nodo in nodos:
                if nodo.posicion == posicion:
                    nodo_en_posicion = nodo
                    break
                    
            if not nodo_en_posicion:
                # Si no se encuentra exactamente la posición, usar el último nodo
                return self.insertar_nodo_al_final(lista_id, vuelo_id)
                
            # Obtener el nodo anterior
            nodo_anterior = self.db.query(NodoDobleVuelos).get(nodo_en_posicion.anterior_id)
            
            # Crear el nuevo nodo
            nuevo_nodo = NodoDobleVuelos(
                vuelo_id=vuelo_id,
                anterior_id=nodo_anterior.id,
                siguiente_id=nodo_en_posicion.id,
                posicion=posicion,
                creado_en=datetime.now(),
                activo=True
            )
            
            self.db.add(nuevo_nodo)
            self.db.flush()  # Para obtener el ID asignado
            
            # Actualizar enlaces
            nodo_anterior.siguiente_id = nuevo_nodo.id
            nodo_en_posicion.anterior_id = nuevo_nodo.id
            
            # Actualizar posiciones de los nodos siguientes
            self._actualizar_posiciones_siguientes(nodo_en_posicion.id)
            
            # Incrementar el tamaño de la lista
            lista.tamanio += 1
            
            self.db.commit()
            self.db.refresh(nuevo_nodo)
            return nuevo_nodo
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
    
    def _actualizar_posiciones_siguientes(self, nodo_id: int, incremento: int = 1):
        """Actualiza las posiciones de los nodos a partir del nodo especificado"""
        nodo_actual = self.db.query(NodoDobleVuelos).get(nodo_id)
        
        # Si es un nodo centinela o no existe, no hay nada que actualizar
        if not nodo_actual or nodo_actual.centinela:
            return
            
        # Actualizar la posición de este nodo y todos los siguientes
        while nodo_actual and not nodo_actual.centinela:
            nodo_actual.posicion += incremento
            nodo_actual = self.db.query(NodoDobleVuelos).get(nodo_actual.siguiente_id)
    
    def extraer_nodo(self, nodo_id: int) -> Tuple[Optional[NodoDobleVuelos], bool]:
        """Extrae un nodo de la lista y lo elimina permanentemente"""
        nodo = self.db.query(NodoDobleVuelos).get(nodo_id)
        if not nodo or nodo.centinela:
            return None, False
            
        try:
            # Obtener nodos adyacentes
            anterior = self.db.query(NodoDobleVuelos).get(nodo.anterior_id)
            siguiente = self.db.query(NodoDobleVuelos).get(nodo.siguiente_id)
            
            # Actualizar enlaces
            anterior.siguiente_id = siguiente.id
            siguiente.anterior_id = anterior.id
            
            # Buscar a qué lista pertenece este nodo
            lista = self.db.query(ListaDobleEnlazadaCentinelas).filter(
                (ListaDobleEnlazadaCentinelas.cabezon_id == anterior.id) | 
                (ListaDobleEnlazadaCentinelas.colon_id == siguiente.id)
            ).first()
            
            if not lista:
                # Buscar otra forma de determinar la lista
                if anterior.centinela:
                    lista = anterior.estado_header
                elif siguiente.centinela:
                    lista = siguiente.estado_trailer
            
            # Guardar una copia del nodo para devolver
            nodo_copia = NodoDobleVuelos(
                id=nodo.id,
                vuelo_id=nodo.vuelo_id,
                posicion=nodo.posicion,
                anterior_id=nodo.anterior_id,
                siguiente_id=nodo.siguiente_id,
                centinela=nodo.centinela,
                creado_en=nodo.creado_en
            )
            
            # Eliminar el nodo permanentemente
            self.db.delete(nodo)
            
            # Actualizar posiciones de los nodos siguientes
            self._actualizar_posiciones_siguientes(siguiente.id, -1)
            
            # Decrementar el tamaño de la lista
            if lista:
                lista.tamanio -= 1
            
            self.db.commit()
            return nodo_copia, True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def obtener_primer_nodo(self, lista_id: int) -> Optional[NodoDobleVuelos]:
        """Obtiene el primer nodo (después del cabezon) de la lista"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return None
            
        # Obtener el cabezon
        cabezon = self.db.query(NodoDobleVuelos).get(lista.cabezon_id)
        if not cabezon:
            return None
        
        # Obtener el primer nodo (después del cabezon)
        primer_nodo = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.id == cabezon.siguiente_id,
            NodoDobleVuelos.centinela == None  # No debe ser centinela
        ).first()
        
        # Si el siguiente es el colón, no hay nodos en la lista
        if primer_nodo and primer_nodo.id != lista.colon_id:
            return primer_nodo
        
        return None

    def obtener_ultimo_nodo(self, lista_id: int) -> Optional[NodoDobleVuelos]:
        """Obtiene el último nodo (antes del colon) de la lista"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return None
            
        # Obtener el colon
        colon = self.db.query(NodoDobleVuelos).get(lista.colon_id)
        if not colon:
            return None
        
        # Obtener el último nodo (antes del colon)
        ultimo_nodo = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.id == colon.anterior_id,
            NodoDobleVuelos.centinela == None  # No debe ser centinela
        ).first()
        
        # Si el anterior es el cabezon, no hay nodos en la lista
        if ultimo_nodo and ultimo_nodo.id != lista.cabezon_id:
            return ultimo_nodo
        
        return None

    def reordenar_lista_por_prioridad(self, lista_id: int) -> bool:
        """Reordena todos los nodos de la lista según prioridad y estado de emergencia"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return False
            
        try:
            # Obtener todos los nodos (excepto centinelas)
            nodos = self.obtener_nodos_de_lista(lista_id)
            if not nodos:
                return True  # No hay nodos que reordenar
                
            # Obtener los nodos centinela
            cabezon = self.db.query(NodoDobleVuelos).get(lista.cabezon_id)
            colon = self.db.query(NodoDobleVuelos).get(lista.colon_id)
            
            # Obtener los vuelos asociados a los nodos
            vuelos_con_nodos = []
            for nodo in nodos:
                vuelo = self.db.query(Vuelo).get(nodo.vuelo_id)
                if vuelo:
                    vuelos_con_nodos.append((vuelo, nodo))
            
            # Ordenar según criterios: emergencia > prioridad > hora_salida
            vuelos_con_nodos.sort(key=lambda x: (
                not x[0].emergencia,  # emergencias primero
                -x[0].prioridad,      # mayor prioridad primero
                x[0].hora_salida      # menor hora de salida primero
            ))
            
            # Reordenar los enlaces de la lista
            nodo_anterior = cabezon
            posicion = 0
            
            for vuelo, nodo in vuelos_con_nodos:
                # Actualizar posición
                nodo.posicion = posicion
                
                # Actualizar enlaces
                nodo_anterior.siguiente_id = nodo.id
                nodo.anterior_id = nodo_anterior.id
                
                nodo_anterior = nodo
                posicion += 1
            
            # Enlazar el último nodo con el colón
            nodo_anterior.siguiente_id = colon.id
            colon.anterior_id = nodo_anterior.id
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def mover_nodo_entre_posiciones(self, lista_id: int, posicion_origen: int, posicion_destino: int) -> bool:
        """
        Mueve un nodo de una posición a otra en la lista.
        
        Args:
            lista_id: ID de la lista donde se moverá el nodo
            posicion_origen: Posición actual del nodo a mover
            posicion_destino: Posición a la que se moverá el nodo
            
        Returns:
            bool: True si el movimiento se realizó correctamente, False en caso contrario
        """
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return False
            
        # Validar posiciones
        if posicion_origen < 0 or posicion_destino < 0:
            return False
            
        # Si las posiciones son iguales, no hay nada que hacer
        if posicion_origen == posicion_destino:
            return True
            
        try:
            # Obtener todos los nodos
            nodos = self.obtener_nodos_de_lista(lista_id)
            
            # Verificar si las posiciones son válidas
            if not nodos or posicion_origen >= len(nodos) or posicion_destino >= len(nodos):
                return False
                
            # Encontrar el nodo en la posición origen
            nodo_origen = None
            for nodo in nodos:
                if nodo.posicion == posicion_origen:
                    nodo_origen = nodo
                    break
                    
            if not nodo_origen:
                return False
                
            # Encontrar el nodo en la posición destino
            nodo_destino = None
            for nodo in nodos:
                if nodo.posicion == posicion_destino:
                    nodo_destino = nodo
                    break
                    
            if not nodo_destino:
                return False
                
            # Obtener los nodos adyacentes al nodo origen
            anterior_origen = self.db.query(NodoDobleVuelos).get(nodo_origen.anterior_id)
            siguiente_origen = self.db.query(NodoDobleVuelos).get(nodo_origen.siguiente_id)
            
            # Desconectar el nodo origen de la lista
            anterior_origen.siguiente_id = siguiente_origen.id
            siguiente_origen.anterior_id = anterior_origen.id
            
            # Si la posición destino es menor que la origen, insertamos antes
            if posicion_destino < posicion_origen:
                anterior_destino = self.db.query(NodoDobleVuelos).get(nodo_destino.anterior_id)
                
                # Conectar el nodo origen en su nueva posición
                nodo_origen.anterior_id = anterior_destino.id
                nodo_origen.siguiente_id = nodo_destino.id
                
                # Actualizar los enlaces
                anterior_destino.siguiente_id = nodo_origen.id
                nodo_destino.anterior_id = nodo_origen.id
            else:
                # Si la posición destino es mayor, insertamos después
                siguiente_destino = self.db.query(NodoDobleVuelos).get(nodo_destino.siguiente_id)
                
                # Conectar el nodo origen en su nueva posición
                nodo_origen.anterior_id = nodo_destino.id
                nodo_origen.siguiente_id = siguiente_destino.id
                
                # Actualizar los enlaces
                nodo_destino.siguiente_id = nodo_origen.id
                siguiente_destino.anterior_id = nodo_origen.id
            
            # Actualizar todas las posiciones
            self._actualizar_todas_posiciones(lista_id)
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _actualizar_todas_posiciones(self, lista_id: int):
        """Actualiza las posiciones de todos los nodos en la lista"""
        lista = self.obtener_lista_por_id(lista_id)
        if not lista:
            return
            
        # Obtener el primer nodo (después del cabezon)
        cabezon = self.db.query(NodoDobleVuelos).get(lista.cabezon_id)
        nodo_actual = self.db.query(NodoDobleVuelos).get(cabezon.siguiente_id)
        
        # Si el primer nodo es el colon, no hay nodos que actualizar
        if nodo_actual.id == lista.colon_id:
            return
            
        # Actualizar las posiciones secuencialmente
        posicion = 0
        while nodo_actual and nodo_actual.id != lista.colon_id:
            nodo_actual.posicion = posicion
            posicion += 1
            nodo_actual = self.db.query(NodoDobleVuelos).get(nodo_actual.siguiente_id)
