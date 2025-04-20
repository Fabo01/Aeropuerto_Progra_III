import customtkinter as ctk
from typing import Any, Optional
from CTkMessagebox import CTkMessagebox
from utils.logger import get_logger

class BaseView(ctk.CTkFrame):
    """Vista base para todas las vistas de la aplicación"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.cliente_api = controller.cliente_api
        
        # Configurar logger
        self.logger = get_logger(self.__class__.__name__)
        
        # Configurar el grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Panel de contenido principal (lo sobrescriben las subclases)
        self.crear_widgets()
    
    def crear_widgets(self):
        """Método para crear los widgets de la vista (a implementar por subclases)"""
        pass
    
    def inicializar(self, *args, **kwargs):
        """Inicializa la vista antes de mostrarla"""
        pass
    
    def mostrar_mensaje(self, titulo: str, mensaje: str, tipo: str = "info") -> None:
        """Muestra un mensaje en una ventana modal"""
        self.logger.info(f"Mostrando mensaje ({tipo}): {titulo} - {mensaje}")
        CTkMessagebox(
            title=titulo,
            message=mensaje,
            icon=tipo  # "info", "warning", "check", "question", "cancel"
        )
    
    def confirmar_accion(self, titulo: str, mensaje: str) -> bool:
        """Muestra un diálogo de confirmación y devuelve True si el usuario confirma"""
        self.logger.info(f"Solicitando confirmación: {titulo} - {mensaje}")
        respuesta = CTkMessagebox(
            title=titulo,
            message=mensaje,
            icon="question",
            option_1="Cancelar",
            option_2="Confirmar"
        )
        resultado = respuesta.get() == "Confirmar"
        self.logger.info(f"Respuesta de confirmación: {resultado}")
        return resultado
    
    def manejar_error_api(self, error, mensaje_predeterminado: str = "Error al comunicarse con el servidor"):
        """Maneja errores de la API y muestra un mensaje al usuario"""
        self.logger.error(f"Error API: {str(error)}")
        
        if hasattr(error, 'response'):
            try:
                error_data = error.response.json()
                if 'detail' in error_data:
                    mensaje_error = error_data['detail']
                    self.logger.error(f"Detalle del error API: {mensaje_error}")
                    self.mostrar_mensaje("Error", mensaje_error, "cancel")
                    return
            except Exception as e:
                self.logger.error(f"Error al procesar respuesta de error: {str(e)}")
                pass
                
        self.logger.error(f"Mostrando mensaje predeterminado: {mensaje_predeterminado}")
        self.mostrar_mensaje("Error", mensaje_predeterminado, "cancel")
