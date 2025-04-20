"""
Módulo de logging para la aplicación
"""
import logging
import os
from datetime import datetime

# Configuración de logs
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIRECTORY = 'logs'

# Crear directorio de logs si no existe
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)

# Nombre del archivo de log con fecha
log_filename = os.path.join(LOG_DIRECTORY, f'app_{datetime.now().strftime("%Y%m%d")}.log')

# Configurar logging global
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # También mostrar logs en consola
    ]
)

def get_logger(name):
    """
    Obtener un logger configurado con el nombre especificado
    
    Args:
        name: Nombre del logger (normalmente __name__)
        
    Returns:
        Un objeto logger configurado
    """
    return logging.getLogger(name)
