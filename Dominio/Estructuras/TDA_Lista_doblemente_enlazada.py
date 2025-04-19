from Estructuras.NodoDoble import NodoDoble

class ListaDoblementeEnlazadaCentinela:
    """Lista doblemente enlazada con nodos centinela (cabezon y colon)."""
    def __init__(self):
        self._cabezon = NodoDoble()
        self._colon = NodoDoble()
        self._cabezon._siguiente = self._colon
        self._colon._anterior = self._cabezon
        self._tamanio = 0

    def __len__(self):
        return self._tamanio

    def esta_vacia(self):
        return self._tamanio == 0

    def insertar_al_frente(self, vuelo):
        """Inserta un vuelo al inicio de la lista (después del cabezon)"""
        self._insertar_entre(vuelo, self._cabezon, self._cabezon._siguiente)

    def insertar_al_final(self, vuelo):
        """Inserta un vuelo al final de la lista (antes del colon)"""
        self._insertar_entre(vuelo, self._colon._anterior, self._colon)

    def insertar_en_posicion(self, vuelo, posicion):
        """Inserta un vuelo en una posición específica de la lista"""
        if posicion <= 0:
            self.insertar_al_frente(vuelo)
        elif posicion >= self._tamanio:
            self.insertar_al_final(vuelo)
        else:
            actual = self._cabezon._siguiente
            for _ in range(posicion):
                actual = actual._siguiente
            self._insertar_entre(vuelo, actual._anterior, actual)

    def insertar_ordenado_por_prioridad(self, vuelo):
        """
        Inserta un vuelo en la posición correcta según su prioridad y emergencia.
        
        Los vuelos de emergencia van al frente de la lista.
        Los vuelos regulares se ordenan por prioridad (mayor prioridad primero)
        y en caso de igual prioridad, por hora de salida.
        """
        # Si es un vuelo de emergencia, insertarlo al frente
        if vuelo.emergencia:
            self.insertar_al_frente(vuelo)
            return

        # Si la lista está vacía o es el primer vuelo no de emergencia, insertarlo al final
        if self.esta_vacia():
            self.insertar_al_final(vuelo)
            return

        # Buscar la posición correcta según prioridad
        actual = self._cabezon._siguiente
        posicion = 0
        
        # Primero pasamos todos los vuelos de emergencia
        while actual != self._colon and actual._elemento.emergencia:
            actual = actual._siguiente
            posicion += 1
            
        # Luego insertamos según prioridad (descendente)
        while actual != self._colon and not actual._elemento.emergencia and actual._elemento.prioridad >= vuelo.prioridad:
            actual = actual._siguiente
            posicion += 1
            
        # Si tienen la misma prioridad, ordenar por hora de salida
        while actual != self._colon and not actual._elemento.emergencia and actual._elemento.prioridad == vuelo.prioridad and actual._elemento.hora_salida <= vuelo.hora_salida:
            actual = actual._siguiente
            posicion += 1
            
        # Insertar en la posición encontrada
        self._insertar_entre(vuelo, actual._anterior, actual)

    def _insertar_entre(self, vuelo, anterior, siguiente):
        """Inserta un vuelo entre dos nodos existentes"""
        nuevo = NodoDoble(vuelo, anterior, siguiente)
        anterior._siguiente = nuevo
        siguiente._anterior = nuevo
        self._tamanio += 1
        return nuevo

    def extraer_de_posicion(self, posicion):
        """Elimina y devuelve el vuelo en la posición especificada"""
        if self.esta_vacia() or posicion < 0 or posicion >= self._tamanio:
            return None
        actual = self._cabezon._siguiente
        for _ in range(posicion):
            actual = actual._siguiente
        return self._eliminar_nodo(actual)

    def _eliminar_nodo(self, nodo):
        """Elimina un nodo de la lista y devuelve su elemento"""
        anterior = nodo._anterior
        siguiente = nodo._siguiente
        anterior._siguiente = siguiente
        siguiente._anterior = anterior
        self._tamanio -= 1
        elemento = nodo._elemento
        nodo._anterior = nodo._siguiente = nodo._elemento = None
        return elemento

    def obtener_primero(self):
        """Devuelve el primer vuelo de la lista sin eliminarlo"""
        if self.esta_vacia():
            return None
        return self._cabezon._siguiente._elemento

    def obtener_ultimo(self):
        """Devuelve el último vuelo de la lista sin eliminarlo"""
        if self.esta_vacia():
            return None
        return self._colon._anterior._elemento
        
    def actualizar_posicion_por_prioridad(self, vuelo):
        """
        Actualiza la posición de un vuelo existente basado en su nueva prioridad o estado de emergencia.
        Este método se llama después de cambiar la prioridad o el estado de emergencia de un vuelo.
        """
        # Buscar el nodo que contiene el vuelo
        nodo_actual = self._cabezon._siguiente
        posicion_actual = 0
        nodo_vuelo = None
        
        while nodo_actual != self._colon:
            if nodo_actual._elemento.id == vuelo.id:
                nodo_vuelo = nodo_actual
                break
            nodo_actual = nodo_actual._siguiente
            posicion_actual += 1
            
        # Si no encontramos el vuelo, no hay nada que hacer
        if not nodo_vuelo:
            return False
            
        # Extraer el vuelo de su posición actual
        vuelo_extraido = self._eliminar_nodo(nodo_vuelo)
        
        # Reinsertar el vuelo en la posición correcta según su nueva prioridad
        self.insertar_ordenado_por_prioridad(vuelo_extraido)
        
        return True

    def mover_vuelo(self, posicion_origen, posicion_destino):
        """Mueve un vuelo de una posición a otra en la lista"""
        if (
            posicion_origen < 0 or posicion_origen >= self._tamanio or
            posicion_destino < 0 or posicion_destino >= self._tamanio or
            posicion_origen == posicion_destino
        ):
            return False
        vuelo = self.extraer_de_posicion(posicion_origen)
        if posicion_destino > posicion_origen:
            posicion_destino -= 1
        self.insertar_en_posicion(vuelo, posicion_destino)
        return True

    def __iter__(self):
        """Permite iterar sobre los vuelos de la lista"""
        actual = self._cabezon._siguiente
        while actual != self._colon:
            yield actual._elemento
            actual = actual._siguiente

    def __str__(self):
        return ' <-> '.join(str(v) for v in self)
