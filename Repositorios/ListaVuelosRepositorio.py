from sqlalchemy.orm import Session
from Modelos.NodoDobleVuelos import NodoDobleVuelos
from Modelos.ListaDobleEnlCent import ListaDobleEnlazadaCentinelas
from Modelos.Vuelo import Vuelo
from typing import List, Optional, Dict, Any
from Utilidades.Excepciones import SynchronizationError
from datetime import datetime
import logging
from Presentacion.API.DTOs.ListaDobleEnlazadaCentinelasDTO import ListaDobleEnlazadaCentinelasDTO
from Presentacion.API.DTOs.NodoDobleVueloDTO import NodoDobleVueloDTO
from Presentacion.API.DTOs.VueloDTO import VueloDTO

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ListaVuelosRepositorio:
    """
    Repositorio para manejar la persistencia de la lista doblemente enlazada con centinelas.
    Garantiza que cada nodo de vuelo tenga su propia fila en la base de datos.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def inicializar_lista(self, nombre: str = "principal") -> ListaDobleEnlazadaCentinelas:
        """
        Inicializa una nueva lista doblemente enlazada en la base de datos.
        Crea los nodos centinelas (cabezon y colon) y establece los enlaces.
        """
        # Verificar si ya existe una lista con este nombre
        lista_existente = self.obtener_estado(nombre)
        if lista_existente:
            return lista_existente
            
        logger.info(f"Inicializando nueva lista '{nombre}'")
        
        # Crear nodos centinelas
        cabezon = NodoDobleVuelos(centinela="cabezon")
        colon = NodoDobleVuelos(centinela="colon")
        
        # Guardar en la base de datos para obtener IDs
        self.db.add(cabezon)
        self.db.add(colon)
        self.db.flush()
        
        # Establecer enlaces entre centinelas
        cabezon.siguiente_id = colon.id
        colon.anterior_id = cabezon.id
        
        # Crear el estado de la lista
        estado = ListaDobleEnlazadaCentinelas(
            nombre=nombre,
            cabezon_id=cabezon.id,
            colon_id=colon.id,
            tamanio=0
        )
        
        self.db.add(estado)
        self.db.commit()
        
        logger.info(f"Lista inicializada: cabezon={cabezon.id}, colon={colon.id}")
        return estado
    
    def obtener_estado(self, nombre: str = "principal") -> Optional[ListaDobleEnlazadaCentinelas]:
        """
        Obtiene el estado de la lista por su nombre.
        """
        return self.db.query(ListaDobleEnlazadaCentinelas).filter(ListaDobleEnlazadaCentinelas.nombre == nombre).first()
    
    def insertar_al_frente(self, vuelo: Vuelo, nombre_lista: str = "principal") -> NodoDobleVuelos:
        """
        Inserta un vuelo al frente de la lista (después del cabezon).
        Crea un nuevo nodo en la BD con ID único.
        """
        # Obtener estado de la lista y centinelas
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            estado = self.inicializar_lista(nombre_lista)
            
        cabezon = estado.header
        logger.info(f"Insertando vuelo {vuelo.id} al frente. Cabezon ID: {cabezon.id}")
        
        # Obtener el nodo que está actualmente al frente (después del cabezon)
        primer_nodo = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == cabezon.siguiente_id).first()
        logger.info(f"Primer nodo actual ID: {primer_nodo.id}, Centinela: {primer_nodo.centinela}")
        
        # Crear nuevo nodo - SIEMPRE con un nuevo ID
        nuevo_nodo = NodoDobleVuelos(
            vuelo_id=vuelo.id,
            anterior_id=cabezon.id,
            siguiente_id=primer_nodo.id,
            posicion=0,
            creado_en=datetime.now(),
            activo=True,
            version=self._obtener_siguiente_version()
        )
        
        self.db.add(nuevo_nodo)
        self.db.flush()  # Asignar ID único
        
        logger.info(f"Nuevo nodo creado (id={nuevo_nodo.id}) al frente para vuelo={vuelo.id}")
        logger.info(f"Enlaces: anterior={nuevo_nodo.anterior_id}, siguiente={nuevo_nodo.siguiente_id}")
        
        # Actualizar enlaces
        cabezon.siguiente_id = nuevo_nodo.id
        primer_nodo.anterior_id = nuevo_nodo.id
        
        # Incrementar tamaño de la lista
        estado.tamanio += 1
        
        # Actualizar posiciones de los demás nodos
        self._actualizar_posiciones(nombre_lista)
        
        self.db.commit()
        return nuevo_nodo
    
    def insertar_al_final(self, vuelo: Vuelo, nombre_lista: str = "principal") -> NodoDobleVuelos:
        """
        Inserta un vuelo al final de la lista (antes del colon).
        Crea un nuevo nodo en la BD con ID único.
        """
        # Obtener estado de la lista y centinelas
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            estado = self.inicializar_lista(nombre_lista)
            
        colon = estado.trailer
        logger.info(f"Insertando vuelo {vuelo.id} al final. Colon ID: {colon.id}")
        
        # Obtener el nodo que está actualmente al final (antes del colon)
        ultimo_nodo = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == colon.anterior_id).first()
        logger.info(f"Último nodo actual ID: {ultimo_nodo.id}, Centinela: {ultimo_nodo.centinela}")
        
        # Crear nuevo nodo - SIEMPRE con un nuevo ID
        nuevo_nodo = NodoDobleVuelos(
            vuelo_id=vuelo.id,
            anterior_id=ultimo_nodo.id,
            siguiente_id=colon.id,
            posicion=estado.tamanio,
            creado_en=datetime.now(),
            activo=True,
            version=self._obtener_siguiente_version()
        )
        
        self.db.add(nuevo_nodo)
        self.db.flush()  # Asignar ID único
        
        logger.info(f"Nuevo nodo creado (id={nuevo_nodo.id}) al final para vuelo={vuelo.id}")
        logger.info(f"Enlaces: anterior={nuevo_nodo.anterior_id}, siguiente={nuevo_nodo.siguiente_id}")
        
        # Actualizar enlaces
        ultimo_nodo.siguiente_id = nuevo_nodo.id
        colon.anterior_id = nuevo_nodo.id
        
        # Incrementar tamaño de la lista
        estado.tamanio += 1
        
        # Verificar integridad de la lista
        self._verificar_integridad_estructura(nombre_lista)
        
        self.db.commit()
        return nuevo_nodo
    
    def insertar_en_posicion(self, vuelo: Vuelo, posicion: int, nombre_lista: str = "principal") -> NodoDobleVuelos:
        """
        Inserta un vuelo en una posición específica de la lista.
        Crea un nuevo nodo en la BD con ID único.
        """
        # Obtener estado de la lista
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            estado = self.inicializar_lista(nombre_lista)
            
        # Validar posición
        if posicion <= 0:
            return self.insertar_al_frente(vuelo, nombre_lista)
        elif posicion >= estado.tamanio:
            return self.insertar_al_final(vuelo, nombre_lista)
            
        # Encontrar el nodo en la posición actual
        nodo_actual = self._obtener_nodo_en_posicion(posicion, nombre_lista)
        if not nodo_actual:
            return self.insertar_al_final(vuelo, nombre_lista)
            
        nodo_anterior = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.anterior_id).first()
        
        # Crear nuevo nodo - SIEMPRE con un nuevo ID
        nuevo_nodo = NodoDobleVuelos(
            vuelo_id=vuelo.id,
            anterior_id=nodo_anterior.id,
            siguiente_id=nodo_actual.id,
            posicion=posicion,
            creado_en=datetime.now()
        )
        
        self.db.add(nuevo_nodo)
        self.db.flush()  # Asignar ID único
        
        logger.info(f"Nuevo nodo creado (id={nuevo_nodo.id}) en posición {posicion} para vuelo={vuelo.id}")
        
        # Actualizar enlaces
        nodo_anterior.siguiente_id = nuevo_nodo.id
        nodo_actual.anterior_id = nuevo_nodo.id
        
        # Incrementar tamaño y actualizar posiciones
        estado.tamanio += 1
        self._actualizar_posiciones(nombre_lista)
        
        self.db.commit()
        return nuevo_nodo
    
    def extraer_de_posicion(self, posicion: int, nombre_lista: str = "principal") -> Optional[Vuelo]:
        """
        Elimina y devuelve el vuelo en la posición especificada.
        """
        # Obtener estado de la lista
        estado = self.obtener_estado(nombre_lista)
        if not estado or estado.tamanio == 0 or posicion < 0 or posicion >= estado.tamanio:
            return None
            
        # Encontrar el nodo a eliminar
        nodo = self._obtener_nodo_en_posicion(posicion, nombre_lista)
        if not nodo:
            return None
            
        # Obtener nodos adyacentes
        nodo_anterior = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo.anterior_id).first()
        nodo_siguiente = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo.siguiente_id).first()
        
        # Obtener vuelo antes de eliminar
        vuelo = nodo.vuelo
        
        # Actualizar enlaces
        nodo_anterior.siguiente_id = nodo_siguiente.id
        nodo_siguiente.anterior_id = nodo_anterior.id
        
        # Eliminar nodo
        self.db.delete(nodo)
        
        # Decrementar tamaño y actualizar posiciones
        estado.tamanio -= 1
        self._actualizar_posiciones(nombre_lista)
        
        self.db.commit()
        return vuelo
    
    def mover_vuelo(self, posicion_origen: int, posicion_destino: int, nombre_lista: str = "principal") -> bool:
        """
        Mueve un vuelo de una posición a otra en la lista.
        Crea un nuevo nodo en lugar de reutilizar el existente.
        """
        # Validar posiciones
        estado = self.obtener_estado(nombre_lista)
        if not estado or estado.tamanio == 0:
            return False
        if (posicion_origen < 0 or posicion_origen >= estado.tamanio or
            posicion_destino < 0 or posicion_destino >= estado.tamanio or
            posicion_origen == posicion_destino):
            return False
            
        # Extraer vuelo de la posición origen
        nodo_origen = self._obtener_nodo_en_posicion(posicion_origen, nombre_lista)
        if not nodo_origen:
            return False
            
        vuelo_id = nodo_origen.vuelo_id
        vuelo = self.db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        
        # Obtener nodos adyacentes para actualizar sus enlaces
        nodo_anterior = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_origen.anterior_id).first()
        nodo_siguiente = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_origen.siguiente_id).first()
        
        # Actualizar enlaces para quitar el nodo
        nodo_anterior.siguiente_id = nodo_siguiente.id
        nodo_siguiente.anterior_id = nodo_anterior.id
        
        # Marcar el nodo original como inactivo, pero preservar sus propiedades
        nodo_origen.activo = False
        
        # Decrementar tamaño temporalmente
        estado.tamanio -= 1
        self.db.flush()
        
        # Ajustar posición de destino si es necesario
        if posicion_destino > posicion_origen:
            posicion_destino -= 1
            
        # Insertar en la nueva posición
        self.insertar_en_posicion(vuelo, posicion_destino, nombre_lista)
        
        # Registrar evento
        logger.info(f"Vuelo {vuelo_id} movido de posición {posicion_origen} a {posicion_destino}")
        
        return True
    
    def obtener_primero(self, nombre_lista: str = "principal") -> Optional[Vuelo]:
        """
        Obtiene el primer vuelo de la lista sin eliminarlo.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado or estado.tamanio == 0:
            return None
            
        cabezon = estado.header
        primer_nodo = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == cabezon.siguiente_id).first()
        
        if primer_nodo and not primer_nodo.centinela and primer_nodo.vuelo_id:
            return self.db.query(Vuelo).filter(Vuelo.id == primer_nodo.vuelo_id).first()
        return None
    
    def obtener_ultimo(self, nombre_lista: str = "principal") -> Optional[Vuelo]:
        """
        Obtiene el último vuelo de la lista sin eliminarlo.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado or estado.tamanio == 0:
            return None
            
        colon = estado.trailer
        ultimo_nodo = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == colon.anterior_id).first()
        
        if ultimo_nodo and not ultimo_nodo.centinela and ultimo_nodo.vuelo_id:
            return self.db.query(Vuelo).filter(Vuelo.id == ultimo_nodo.vuelo_id).first()
        return None
    
    def obtener_todos(self, nombre_lista: str = "principal", solo_activos: bool = True) -> List[Vuelo]:
        """
        Obtiene todos los vuelos en la lista en orden.
        
        Args:
            nombre_lista: Nombre de la lista
            solo_activos: Si es True, solo devuelve los nodos activos (estado actual)
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            estado = self.inicializar_lista(nombre_lista)
            return []
            
        # Iniciar recorrido desde el cabezon
        cabezon = estado.header
        nodo_actual = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.id == cabezon.siguiente_id
        ).first()
        
        vuelos = []
        # Filtrar por activos si se solicita
        filtro_adicional = (NodoDobleVuelos.activo == True) if solo_activos else None
        
        while nodo_actual and not nodo_actual.centinela:
            if nodo_actual.vuelo_id and (not solo_activos or nodo_actual.activo):
                vuelo = self.db.query(Vuelo).filter(Vuelo.id == nodo_actual.vuelo_id).first()
                if vuelo:
                    vuelos.append(vuelo)
            
            # Avanzar al siguiente nodo
            nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.siguiente_id).first()
        
        return vuelos
    
    def _obtener_nodo_en_posicion(self, posicion: int, nombre_lista: str = "principal") -> Optional[NodoDobleVuelos]:
        """
        Obtiene el nodo en la posición especificada.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado or estado.tamanio == 0 or posicion < 0 or posicion >= estado.tamanio:
            return None
            
        # Buscar el nodo en la posición especificada
        nodos = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.posicion == posicion,
            NodoDobleVuelos.centinela == None
        ).first()
        
        if nodos:
            return nodos
        
        # Si no se encuentra por posición, recorrer la lista
        cabezon = estado.header
        nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == cabezon.siguiente_id).first()
        
        contador = 0
        while nodo_actual and not nodo_actual.centinela:
            if contador == posicion:
                return nodo_actual
            contador += 1
            nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.siguiente_id).first()
        
        return None
    
    def _actualizar_posiciones(self, nombre_lista: str = "principal"):
        """
        Actualiza las posiciones de todos los nodos en la lista.
        Garantiza que cada nodo tenga una posición acorde a su ubicación en la lista.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            return
            
        # Iniciar recorrido desde el cabezon
        cabezon = estado.header
        nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == cabezon.siguiente_id).first()
        
        posicion = 0
        while nodo_actual and not nodo_actual.centinela:
            # Asegurarse de que cada nodo tenga posición actualizada
            if nodo_actual.posicion != posicion:
                logger.debug(f"Actualizando posición de nodo id={nodo_actual.id} de {nodo_actual.posicion} a {posicion}")
                nodo_actual.posicion = posicion
            posicion += 1
            
            # Obtener el siguiente nodo por su ID
            siguiente_id = nodo_actual.siguiente_id
            nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == siguiente_id).first()
        
        # Actualizar tamaño si es necesario
        if estado.tamanio != posicion:
            logger.info(f"Actualizando tamaño de lista de {estado.tamanio} a {posicion}")
            estado.tamanio = posicion
            
        self.db.flush()
    
    def eliminar_lista(self, nombre_lista: str = "principal"):
        """
        Elimina toda la lista incluyendo sus nodos.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            return
            
        # Eliminar todos los nodos (excepto centinelas)
        nodos = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.centinela == None
        ).all()
        
        for nodo in nodos:
            self.db.delete(nodo)
        
        # Eliminar centinelas
        if estado.header:
            self.db.delete(estado.header)
        if estado.trailer:
            self.db.delete(estado.trailer)
        
        # Eliminar estado
        self.db.delete(estado)
        self.db.commit()
        
    def sincronizar_con_memoria(self, vuelos_memoria: List[Vuelo], nombre_lista: str = "principal"):
        """
        Sincroniza la lista en base de datos con la versión en memoria.
        Asegura que cada nodo tenga persistencia y un ID único.
        """
        try:
            # En lugar de eliminar y recrear, vamos a actualizar la estructura existente
            estado = self.obtener_estado(nombre_lista)
            if not estado:
                estado = self.inicializar_lista(nombre_lista)
            
            # Primero, guardamos los vuelos que podrían no estar en la BD
            for vuelo in vuelos_memoria:
                if not vuelo.id:  # Si el vuelo no tiene ID, necesita ser persistido
                    self.db.add(vuelo)
            self.db.flush()
            
            # Eliminar todos los nodos no centinelas actuales
            nodos = self.db.query(NodoDobleVuelos).filter(
                NodoDobleVuelos.centinela == None
            ).all()
            
            for nodo in nodos:
                self.db.delete(nodo)
            
            # Reiniciar la estructura
            cabezon = estado.header
            colon = estado.trailer
            cabezon.siguiente_id = colon.id
            colon.anterior_id = cabezon.id
            
            self.db.flush()
            
            # Reconstruir la lista con todos los vuelos de memoria
            nodo_anterior = cabezon
            posicion = 0
            
            for vuelo in vuelos_memoria:
                # Crear nuevo nodo con ID único
                nuevo_nodo = NodoDobleVuelos(
                    vuelo_id=vuelo.id,
                    anterior_id=nodo_anterior.id,
                    siguiente_id=colon.id,
                    posicion=posicion
                )
                
                self.db.add(nuevo_nodo)
                self.db.flush()  # Asegurar que tenga ID
                
                # Actualizar enlaces
                nodo_anterior.siguiente_id = nuevo_nodo.id
                colon.anterior_id = nuevo_nodo.id
                
                # Preparar para la siguiente iteración
                nodo_anterior = nuevo_nodo
                posicion += 1
            
            # Actualizar el tamaño de la lista
            estado.tamanio = len(vuelos_memoria)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise SynchronizationError(f"Error al sincronizar con memoria: {str(e)}")
    
    def sincronizar_estructura_completa(self, lista_memoria, nombre_lista: str = "principal"):
        """
        Sincroniza toda la estructura de la lista doblemente enlazada en memoria a la BD.
        Asegura que cada nodo tenga un ID único y que las posiciones sean correctas.
        """
        try:
            # Obtener el estado de la lista
            estado = self.obtener_estado(nombre_lista)
            if not estado:
                estado = self.inicializar_lista(nombre_lista)
                return True
                
            # Preservar centinelas
            cabezon = estado.header
            colon = estado.trailer
            
            # Calcular nueva versión
            nueva_version = 1
            max_version = self.db.query(NodoDobleVuelos).filter(
                NodoDobleVuelos.centinela == None
            ).order_by(NodoDobleVuelos.version.desc()).first()
            
            if max_version:
                nueva_version = max_version.version + 1
            
            # Marcar todos los nodos activos como históricos, pero preservar sus datos
            nodos_activos = self.db.query(NodoDobleVuelos).filter(
                NodoDobleVuelos.centinela == None,
                NodoDobleVuelos.activo == True
            ).all()
            
            for nodo in nodos_activos:
                # Conservar los enlaces pero marcarlo como inactivo
                nodo.activo = False
            
            # Reconectar centinelas
            cabezon.siguiente_id = colon.id
            colon.anterior_id = cabezon.id
            # Los centinelas siempre están activos
            cabezon.activo = True
            colon.activo = True
            
            estado.tamanio = 0
            
            self.db.flush()
            
            # Si la lista en memoria está vacía, terminamos
            if len(lista_memoria) == 0:
                self.db.commit()
                return True
                
            # Recorrer la lista en memoria y crear nodos en BD
            nodo_memoria = lista_memoria._cabezon._siguiente
            nodo_anterior_bd = cabezon
            posicion = 0
            
            # Crear todos los nodos primero sin establecer los enlaces finales
            nodos_creados = []
            
            while nodo_memoria != lista_memoria._colon:
                vuelo = nodo_memoria._elemento
                # Asegurar que el vuelo esté persistido
                if not vuelo.id:
                    self.db.add(vuelo)
                    self.db.flush()
                
                # Crear nodo en BD con ID único - Inicialmente solo conectamos con el anterior
                nuevo_nodo = NodoDobleVuelos(
                    vuelo_id=vuelo.id,
                    anterior_id=nodo_anterior_bd.id,  # Enlace con el nodo anterior
                    siguiente_id=None,  # Temporalmente null hasta establecer todas las conexiones
                    posicion=posicion,
                    creado_en=datetime.now(),
                    activo=True,  # Marcado como activo
                    version=nueva_version
                )
                
                self.db.add(nuevo_nodo)
                self.db.flush()  # Asegurar que tenga ID
                
                nodos_creados.append(nuevo_nodo)
                logger.info(f"Sincronización: Creado nodo id={nuevo_nodo.id} para vuelo id={vuelo.id} (versión {nueva_version})")
                
                # Actualizar referencia del nodo anterior a este nuevo nodo
                nodo_anterior_bd.siguiente_id = nuevo_nodo.id
                
                # Preparar para el siguiente nodo
                nodo_anterior_bd = nuevo_nodo
                nodo_memoria = nodo_memoria._siguiente
                posicion += 1
            
            # Ahora que todos los nodos están creados, establecer sus conexiones finales
            for i, nodo in enumerate(nodos_creados):
                # Establecer el enlace siguiente
                if i < len(nodos_creados) - 1:
                    nodo.siguiente_id = nodos_creados[i + 1].id
                else:
                    # El último nodo apunta al colón
                    nodo.siguiente_id = colon.id
                    colon.anterior_id = nodo.id
            
            # Actualizar el tamaño de la lista
            estado.tamanio = len(nodos_creados)
            
            # Verificar la integridad de la estructura
            self._verificar_integridad_estructura(nombre_lista)
            
            self.db.commit()
            logger.info(f"Sincronización completada: {estado.tamanio} nodos creados en versión {nueva_version}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error en sincronización: {str(e)}")
            raise SynchronizationError(f"Error al sincronizar estructura completa: {str(e)}")

    def _verificar_integridad_estructura(self, nombre_lista: str = "principal"):
        """
        Verifica la integridad de la estructura de la lista en la base de datos.
        Asegura que todos los nodos estén correctamente enlazados.
        """
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            return
            
        cabezon = estado.header
        colon = estado.trailer
        
        # Verificar que cabezon apunte al primer nodo (o al colon si está vacía)
        if cabezon.siguiente_id is None:
            logger.error("Error de integridad: cabezón no tiene siguiente")
            cabezon.siguiente_id = colon.id
            colon.anterior_id = cabezon.id
            estado.tamanio = 0
            return
        
        # Recorrer desde cabezon en dirección siguiente
        nodo_actual = cabezon
        contador = 0
        nodos_visitados = set()
        
        while True:
            # Evitar ciclos infinitos
            if nodo_actual.id in nodos_visitados:
                logger.error(f"Ciclo detectado en la estructura, nodo id={nodo_actual.id}")
                break
                
            nodos_visitados.add(nodo_actual.id)
            
            # Verificar que el nodo tenga un siguiente
            if nodo_actual.siguiente_id is None:
                logger.error(f"Nodo id={nodo_actual.id} no tiene siguiente, reparando...")
                nodo_actual.siguiente_id = colon.id
                colon.anterior_id = nodo_actual.id
                break
            
            # Obtener el siguiente nodo
            siguiente = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.siguiente_id).first()
            if not siguiente:
                logger.error(f"No se encontró el nodo siguiente id={nodo_actual.siguiente_id}, reparando...")
                nodo_actual.siguiente_id = colon.id
                colon.anterior_id = nodo_actual.id
                break
                
            # Verificar que el siguiente apunte a este como anterior
            if siguiente.anterior_id != nodo_actual.id:
                logger.error(f"Inconsistencia: nodo id={siguiente.id} no apunta a nodo id={nodo_actual.id} como anterior")
                siguiente.anterior_id = nodo_actual.id
            
            # Si llegamos al colon, hemos terminado
            if siguiente.centinela == "colon":
                break
                
            # Avanzar al siguiente nodo
            nodo_actual = siguiente
            contador += 1
            
            # Protección contra recorridos muy largos
            if contador > 1000:
                logger.error("Posible recorrido infinito detectado")
                break
        
        # Actualizar tamaño si es necesario
        if estado.tamanio != contador:
            logger.info(f"Corrigiendo tamaño de lista de {estado.tamanio} a {contador}")
            estado.tamanio = contador
            
        logger.info(f"Verificación de integridad completada: {contador} nodos en la lista")
    
    def obtener_historial_nodos(self, vuelo_id: int = None) -> List[NodoDobleVuelos]:
        """
        Obtiene el historial de todos los nodos para un vuelo específico o todos los vuelos.
        
        Args:
            vuelo_id: ID del vuelo (opcional)
        
        Returns:
            Lista de nodos ordenados por versión y posición
        """
        query = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.centinela == None
        )
        
        if vuelo_id is not None:
            query = query.filter(NodoDobleVuelos.vuelo_id == vuelo_id)
        
        return query.order_by(NodoDobleVuelos.version, NodoDobleVuelos.posicion).all()
    
    def _obtener_siguiente_version(self) -> int:
        """Obtiene la siguiente versión para un nuevo nodo"""
        max_version = self.db.query(NodoDobleVuelos).filter(
            NodoDobleVuelos.centinela == None
        ).order_by(NodoDobleVuelos.version.desc()).first()
        
        if max_version and hasattr(max_version, 'version'):
            return max_version.version + 1
        return 1

    def _verificar_nodos_estructura(self, nombre_lista: str = "principal"):
        """Verifica y lista todos los nodos de la estructura para diagnóstico"""
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            logger.error("No se encontró estado de lista")
            return
            
        cabezon = estado.header
        colon = estado.trailer
        
        logger.info(f"Estado de lista: {nombre_lista}, tamaño: {estado.tamanio}")
        logger.info(f"Cabezon: ID={cabezon.id}, siguiente_id={cabezon.siguiente_id}")
        logger.info(f"Colon: ID={colon.id}, anterior_id={colon.anterior_id}")
        
        # Recorrer y listar todos los nodos
        nodo_actual = cabezon
        count = 0
        
        while nodo_actual and count < 100:  # Límite de seguridad
            siguiente = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.siguiente_id).first()
            
            if not siguiente:
                logger.error(f"Nodo {nodo_actual.id} apunta a un siguiente_id={nodo_actual.siguiente_id} que no existe")
                break
                
            logger.info(f"Nodo {nodo_actual.id} -> Siguiente: {siguiente.id}")
            
            if siguiente.anterior_id != nodo_actual.id:
                logger.error(f"Inconsistencia: Nodo {siguiente.id} tiene anterior_id={siguiente.anterior_id}, debería ser {nodo_actual.id}")
                
            nodo_actual = siguiente
            count += 1
            
            if nodo_actual.id == colon.id:
                logger.info("Recorrido completado hasta el colón")
                break
                
        if count >= 100:
            logger.error("Posible ciclo infinito en la estructura")

    def obtener_lista_dto(self, nombre_lista: str = "principal") -> ListaDobleEnlazadaCentinelasDTO:
        estado = self.obtener_estado(nombre_lista)
        if not estado:
            return None
        nodos = []
        cabezon = estado.header
        nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == cabezon.siguiente_id).first()
        while nodo_actual and not nodo_actual.centinela:
            vuelo = nodo_actual.vuelo
            vuelo_dto = VueloDTO.model_validate(vuelo)
            nodo_dto = NodoDobleVueloDTO(
                id=nodo_actual.id,
                vuelo=vuelo_dto,
                posicion=nodo_actual.posicion,
                lista_id=estado.id,
                anterior_id=nodo_actual.anterior_id,
                siguiente_id=nodo_actual.siguiente_id
            )
            nodos.append(nodo_dto)
            nodo_actual = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_actual.siguiente_id).first()
        return ListaDobleEnlazadaCentinelasDTO(
            id=estado.id,
            nombre=estado.nombre,
            nodos=nodos
        )

    def obtener_nodo_dto(self, nodo_id: int) -> NodoDobleVueloDTO:
        nodo = self.db.query(NodoDobleVuelos).filter(NodoDobleVuelos.id == nodo_id).first()
        if not nodo or not nodo.vuelo:
            return None
        vuelo_dto = VueloDTO.model_validate(nodo.vuelo)
        return NodoDobleVueloDTO(
            id=nodo.id,
            vuelo=vuelo_dto,
            posicion=nodo.posicion,
            lista_id=nodo.estado_header.id if nodo.estado_header else None,
            anterior_id=nodo.anterior_id,
            siguiente_id=nodo.siguiente_id
        )