import requests
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from utils.logger import get_logger

class ClienteAPI:
    """Cliente para comunicarse con la API del aeropuerto"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.logger = get_logger(self.__class__.__name__)
        self.logger.info(f"Cliente API inicializado con URL base: {base_url}")
        
    # ===== Métodos para gestionar vuelos =====
    def obtener_vuelos(self) -> List[Dict[str, Any]]:
        """Obtiene todos los vuelos"""
        self.logger.debug("Solicitando lista de vuelos")
        try:
            response = requests.get(f"{self.base_url}/vuelos/")
            response.raise_for_status()
            vuelos = response.json()
            self.logger.debug(f"Obtenidos {len(vuelos)} vuelos")
            return vuelos
        except Exception as e:
            self.logger.error(f"Error al obtener vuelos: {str(e)}")
            raise
    
    def obtener_vuelo(self, vuelo_id: int) -> Dict[str, Any]:
        """Obtiene un vuelo específico por ID"""
        self.logger.debug(f"Solicitando vuelo con ID: {vuelo_id}")
        try:
            response = requests.get(f"{self.base_url}/vuelos/{vuelo_id}")
            response.raise_for_status()
            vuelo = response.json()
            self.logger.debug(f"Obtenido vuelo: {vuelo.get('numero_vuelo')}")
            return vuelo
        except Exception as e:
            self.logger.error(f"Error al obtener vuelo {vuelo_id}: {str(e)}")
            raise
    
    def crear_vuelo(self, vuelo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un nuevo vuelo"""
        self.logger.debug(f"Creando vuelo con datos: {vuelo_data}")
        # Convertir fechas a formato ISO si son objetos datetime
        if isinstance(vuelo_data.get('hora_salida'), datetime):
            vuelo_data['hora_salida'] = vuelo_data['hora_salida'].isoformat()
        if isinstance(vuelo_data.get('hora_llegada'), datetime):
            vuelo_data['hora_llegada'] = vuelo_data['hora_llegada'].isoformat()
            
        # Asegurarse de no enviar el campo 'id' si existe en el diccionario
        if 'id' in vuelo_data:
            del vuelo_data['id']
            
        try:
            response = requests.post(f"{self.base_url}/vuelos/", json=vuelo_data)
            response.raise_for_status()
            vuelo = response.json()
            self.logger.debug(f"Vuelo creado: {vuelo.get('numero_vuelo')}")
            return vuelo
        except Exception as e:
            self.logger.error(f"Error al crear vuelo: {str(e)}")
            # Registrar información detallada del error si es una respuesta HTTP
            if hasattr(e, 'response') and e.response is not None:
                self.manejar_respuesta_error(e.response)
            raise
    
    def actualizar_vuelo(self, vuelo_id: int, vuelo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un vuelo existente"""
        self.logger.debug(f"Actualizando vuelo con ID: {vuelo_id} y datos: {vuelo_data}")
        
        # Asegurarse de que el ID esté incluido en los datos enviados
        vuelo_data["id"] = vuelo_id
        
        # Convertir fechas a formato ISO si son objetos datetime
        if isinstance(vuelo_data.get('hora_salida'), datetime):
            vuelo_data['hora_salida'] = vuelo_data['hora_salida'].isoformat()
        if isinstance(vuelo_data.get('hora_llegada'), datetime):
            vuelo_data['hora_llegada'] = vuelo_data['hora_llegada'].isoformat()
        try:
            response = requests.put(f"{self.base_url}/vuelos/{vuelo_id}", json=vuelo_data)
            response.raise_for_status()
            vuelo = response.json()
            self.logger.debug(f"Vuelo actualizado: {vuelo.get('numero_vuelo')}")
            return vuelo
        except Exception as e:
            self.logger.error(f"Error al actualizar vuelo {vuelo_id}: {str(e)}")
            # Registrar información detallada del error si es una respuesta HTTP
            if hasattr(e, 'response') and e.response is not None:
                self.manejar_respuesta_error(e.response)
            raise
    
    def eliminar_vuelo(self, vuelo_id: int) -> Dict[str, Any]:
        """Elimina un vuelo"""
        self.logger.debug(f"Eliminando vuelo con ID: {vuelo_id}")
        try:
            response = requests.delete(f"{self.base_url}/vuelos/{vuelo_id}")
            response.raise_for_status()
            resultado = response.json() if response.text else {"message": "Vuelo eliminado correctamente"}
            self.logger.debug(f"Vuelo eliminado: {vuelo_id}")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al eliminar vuelo {vuelo_id}: {str(e)}")
            raise
    
    # ===== Métodos para gestionar la lista doblemente enlazada =====
    def obtener_lista(self) -> Dict[str, Any]:
        """Obtiene la lista principal con todos sus nodos"""
        self.logger.debug("Solicitando lista principal de nodos")
        try:
            response = requests.get(f"{self.base_url}/lista/")
            response.raise_for_status()
            lista = response.json()
            self.logger.debug("Lista obtenida")
            return lista
        except Exception as e:
            self.logger.error(f"Error al obtener lista: {str(e)}")
            raise
    
    def insertar_vuelo_al_frente(self, vuelo_id: int) -> Dict[str, Any]:
        """Inserta un vuelo al principio de la lista"""
        self.logger.debug(f"Insertando vuelo al frente con ID: {vuelo_id}")
        try:
            response = requests.post(f"{self.base_url}/lista/insertar-al-frente?vuelo_id={vuelo_id}")
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Vuelo insertado al frente")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al insertar vuelo al frente: {str(e)}")
            raise
    
    def insertar_vuelo_al_final(self, vuelo_id: int) -> Dict[str, Any]:
        """Inserta un vuelo al final de la lista"""
        self.logger.debug(f"Insertando vuelo al final con ID: {vuelo_id}")
        try:
            response = requests.post(f"{self.base_url}/lista/insertar-al-final?vuelo_id={vuelo_id}")
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Vuelo insertado al final")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al insertar vuelo al final: {str(e)}")
            raise
    
    def insertar_vuelo_ordenado(self, vuelo_id: int, posicion: Optional[int] = None) -> Dict[str, Any]:
        """Inserta un vuelo en la lista ordenado por prioridad o en una posición específica"""
        self.logger.debug(f"Insertando vuelo ordenado con ID: {vuelo_id} en posición: {posicion}")
        url = f"{self.base_url}/lista/insertar-ordenado?vuelo_id={vuelo_id}"
        if posicion is not None:
            url += f"&posicion={posicion}"
        try:
            response = requests.post(url)
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Vuelo insertado ordenadamente")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al insertar vuelo ordenado: {str(e)}")
            raise
    
    def extraer_vuelo_de_posicion(self, posicion: int) -> Dict[str, Any]:
        """Extrae un vuelo de una posición específica"""
        self.logger.debug(f"Extrayendo vuelo de la posición: {posicion}")
        try:
            response = requests.delete(f"{self.base_url}/lista/extraer/{posicion}")
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Vuelo extraído de la posición")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al extraer vuelo de la posición {posicion}: {str(e)}")
            raise
    
    def reordenar_lista(self) -> Dict[str, Any]:
        """Reordena la lista según prioridad y estado de emergencia"""
        self.logger.debug("Reordenando lista")
        try:
            response = requests.post(f"{self.base_url}/lista/reordenar")
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Lista reordenada")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al reordenar lista: {str(e)}")
            raise
    
    def obtener_cantidad_nodos(self) -> int:
        """Obtiene la cantidad de nodos en la lista"""
        self.logger.debug("Solicitando cantidad de nodos en la lista")
        try:
            response = requests.get(f"{self.base_url}/lista/cantidad")
            response.raise_for_status()
            cantidad = response.json()
            self.logger.debug(f"Cantidad de nodos: {cantidad}")
            return cantidad
        except Exception as e:
            self.logger.error(f"Error al obtener cantidad de nodos: {str(e)}")
            raise
    
    def obtener_primer_vuelo(self) -> Optional[Dict[str, Any]]:
        """Obtiene el primer vuelo de la lista"""
        self.logger.debug("Solicitando primer vuelo de la lista")
        try:
            response = requests.get(f"{self.base_url}/lista/primer-vuelo")
            response.raise_for_status()
            vuelo = response.json()
            self.logger.debug("Primer vuelo obtenido")
            return vuelo
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Es normal que no haya vuelos en la lista
                self.logger.info("No hay vuelos en la lista para obtener como primer vuelo")
                return None
            self.logger.error(f"Error al obtener primer vuelo: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error al obtener primer vuelo: {str(e)}")
            raise
    
    def obtener_ultimo_vuelo(self) -> Optional[Dict[str, Any]]:
        """Obtiene el último vuelo de la lista"""
        self.logger.debug("Solicitando último vuelo de la lista")
        try:
            response = requests.get(f"{self.base_url}/lista/ultimo-vuelo")
            response.raise_for_status()
            vuelo = response.json()
            self.logger.debug("Último vuelo obtenido")
            return vuelo
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Es normal que no haya vuelos en la lista
                self.logger.info("No hay vuelos en la lista para obtener como último vuelo")
                return None
            self.logger.error(f"Error al obtener último vuelo: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error al obtener último vuelo: {str(e)}")
            raise
    
    def mover_nodo(self, posicion_origen: int, posicion_destino: int) -> Dict[str, Any]:
        """Mueve un nodo de una posición a otra"""
        self.logger.debug(f"Moviendo nodo de posición {posicion_origen} a {posicion_destino}")
        try:
            response = requests.post(
                f"{self.base_url}/lista/mover-nodo?posicion_origen={posicion_origen}&posicion_destino={posicion_destino}"
            )
            response.raise_for_status()
            resultado = response.json()
            self.logger.debug("Nodo movido")
            return resultado
        except Exception as e:
            self.logger.error(f"Error al mover nodo de {posicion_origen} a {posicion_destino}: {str(e)}")
            raise
    
    def manejar_respuesta_error(self, response):
        """Registra información detallada sobre errores de la API"""
        try:
            self.logger.error(f"Error API - Código: {response.status_code}, URL: {response.url}")
            self.logger.error(f"Headers: {response.headers}")
            self.logger.error(f"Contenido: {response.text}")
            
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                self.logger.error(f"Datos de error JSON: {error_data}")
        except Exception as e:
            self.logger.error(f"Error al procesar respuesta de error: {str(e)}")
