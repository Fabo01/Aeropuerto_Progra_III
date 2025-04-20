"""
Funciones de validación para formularios y entrada de datos.
"""
from datetime import datetime
from typing import Tuple, Optional
from utils.logger import get_logger

# Crear logger
logger = get_logger(__name__)

def validar_texto_no_vacio(valor: str) -> Tuple[bool, Optional[str]]:
    """Valida que un texto no esté vacío"""
    logger.debug(f"Validando texto no vacío: '{valor}'")
    if not valor or not valor.strip():
        logger.debug("Validación fallida: texto vacío")
        return False, "Este campo no puede estar vacío"
    logger.debug("Validación exitosa: texto no vacío")
    return True, None

def validar_numero_entero(valor: str) -> Tuple[bool, Optional[str]]:
    """Valida que un texto sea un número entero"""
    logger.debug(f"Validando número entero: '{valor}'")
    if not valor or not valor.strip():
        logger.debug("Validación fallida: texto vacío")
        return False, "Este campo no puede estar vacío"
    try:
        int(valor)
        logger.debug("Validación exitosa: es número entero")
        return True, None
    except ValueError:
        logger.debug("Validación fallida: no es número entero")
        return False, "Debe ingresar un número entero"

def validar_prioridad(valor: str) -> Tuple[bool, Optional[str]]:
    """Valida que un texto sea un número entero entre 0 y 100"""
    logger.debug(f"Validando prioridad: '{valor}'")
    valido, mensaje = validar_numero_entero(valor)
    if not valido:
        return valido, mensaje
    
    try:
        num = int(valor)
        if num < 0 or num > 100:
            logger.debug(f"Validación fallida: prioridad fuera de rango ({num})")
            return False, "La prioridad debe estar entre 0 y 100"
        logger.debug("Validación exitosa: prioridad en rango")
        return True, None
    except ValueError:
        logger.debug("Validación fallida: no es número entero")
        return False, "La prioridad debe ser un número entero"

def validar_fecha_hora(valor: str) -> Tuple[bool, Optional[str]]:
    """Valida que un texto sea una fecha y hora válida"""
    logger.debug(f"Validando fecha/hora: '{valor}'")
    if not valor or not valor.strip():
        logger.debug("Validación fallida: texto vacío")
        return False, "Este campo no puede estar vacío"
    
    try:
        # Intentar parsear la fecha y hora
        datetime.fromisoformat(valor)
        logger.debug("Validación exitosa: formato ISO")
        return True, None
    except ValueError:
        try:
            # Intentar con formato más común
            datetime.strptime(valor, "%Y-%m-%d %H:%M")
            logger.debug("Validación exitosa: formato YYYY-MM-DD HH:MM")
            return True, None
        except ValueError:
            logger.debug(f"Validación fallida: formato de fecha/hora inválido '{valor}'")
            return False, "Formato inválido. Use YYYY-MM-DD HH:MM"

def validar_estado_vuelo(valor: str) -> Tuple[bool, Optional[str]]:
    """Valida que el estado del vuelo sea válido"""
    logger.debug(f"Validando estado de vuelo: '{valor}'")
    estados_validos = ['programado', 'retrasado', 'cancelado']
    if valor not in estados_validos:
        logger.debug(f"Validación fallida: estado inválido '{valor}'")
        return False, f"Estado inválido. Debe ser: {', '.join(estados_validos)}"
    logger.debug("Validación exitosa: estado válido")
    return True, None

def convertir_a_fecha_hora(valor: str) -> datetime:
    """Convierte un texto a un objeto datetime"""
    logger.debug(f"Convirtiendo texto a fecha/hora: '{valor}'")
    try:
        dt = datetime.fromisoformat(valor)
        logger.debug(f"Conversión exitosa (ISO): {dt}")
        return dt
    except ValueError:
        try:
            dt = datetime.strptime(valor, "%Y-%m-%d %H:%M")
            logger.debug(f"Conversión exitosa (YYYY-MM-DD HH:MM): {dt}")
            return dt
        except ValueError:
            # Si todo falla, retornar la fecha actual
            now = datetime.now()
            logger.warning(f"Error en conversión, usando fecha actual: {now}")
            return now
