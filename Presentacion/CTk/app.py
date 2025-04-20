import os
import sys
import customtkinter as ctk
from PIL import Image
from cliente_api import ClienteAPI
from utils.estilos import aplicar_estilo, COLORES

class App(ctk.CTk):
    """Aplicación principal con navegación entre vistas"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración básica de la ventana
        self.title("Sistema de Control de Aeropuerto")
        self.geometry("1100x700")
        self.minsize(800, 600)
        
        # Inicializar el cliente API
        self.cliente_api = ClienteAPI()
        
        # Configurar el grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Crear el menú lateral
        self.crear_menu_lateral()
        
        # Crear el contenedor de vistas
        self.frame_principal = ctk.CTkFrame(self, corner_radius=0)
        self.frame_principal.grid(row=0, column=1, sticky="nsew")
        self.frame_principal.grid_columnconfigure(0, weight=1)
        self.frame_principal.grid_rowconfigure(0, weight=1)
        
        # Inicializar las vistas
        self.vistas = {}
        self.crear_vistas()
        
        # Mostrar vista inicial (dashboard)
        self.mostrar_vista("dashboard")
    
    def crear_menu_lateral(self):
        """Crea el menú lateral con botones de navegación"""
        frame_menu = ctk.CTkFrame(self, width=200, corner_radius=0)
        frame_menu.grid(row=0, column=0, sticky="nsew")
        frame_menu.grid_rowconfigure(5, weight=1)  # Espacio vacío al final
        
        # Logo o título del sistema
        label_logo = ctk.CTkLabel(
            frame_menu, 
            text="Control Aeropuerto",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        label_logo.grid(row=0, column=0, padx=20, pady=20)
        
        # Botones de navegación
        self.btn_dashboard = ctk.CTkButton(
            frame_menu,
            text="Dashboard",
            command=lambda: self.mostrar_vista("dashboard")
        )
        aplicar_estilo(self.btn_dashboard, "button")
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_lista_vuelos = ctk.CTkButton(
            frame_menu,
            text="Lista de Vuelos",
            command=lambda: self.mostrar_vista("lista_vuelos")
        )
        aplicar_estilo(self.btn_lista_vuelos, "button")
        self.btn_lista_vuelos.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_crear_vuelo = ctk.CTkButton(
            frame_menu,
            text="Crear Vuelo",
            command=lambda: self.mostrar_vista("detalle_vuelo", None)
        )
        aplicar_estilo(self.btn_crear_vuelo, "button")
        self.btn_crear_vuelo.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_gestion_lista = ctk.CTkButton(
            frame_menu,
            text="Gestión de Lista",
            command=lambda: self.mostrar_vista("gestion_lista")
        )
        aplicar_estilo(self.btn_gestion_lista, "button")
        self.btn_gestion_lista.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        # Información de la app en la parte inferior
        info_label = ctk.CTkLabel(
            frame_menu,
            text="v1.0.0\nDesarrollado por\nEquipo RCP",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        info_label.grid(row=6, column=0, padx=20, pady=10, sticky="s")
    
    def crear_vistas(self):
        """Inicializa todas las vistas disponibles"""
        # Importamos aquí para evitar importaciones circulares
        from vistas.dashboard import DashboardView
        from vistas.lista_vuelos import ListaVuelosView
        from vistas.detalle_vuelo import DetalleVueloView
        from vistas.gestion_lista import GestionListaView
        
        self.vistas = {
            "dashboard": DashboardView(
                parent=self.frame_principal,
                controller=self
            ),
            "lista_vuelos": ListaVuelosView(
                parent=self.frame_principal,
                controller=self
            ),
            "detalle_vuelo": DetalleVueloView(
                parent=self.frame_principal,
                controller=self
            ),
            "gestion_lista": GestionListaView(
                parent=self.frame_principal,
                controller=self
            )
        }
        
        # Ocultar todas las vistas inicialmente
        for vista in self.vistas.values():
            vista.grid_forget()
    
    def mostrar_vista(self, nombre_vista, *args, **kwargs):
        """Muestra una vista específica y oculta las demás"""
        # Ocultar todas las vistas
        for vista in self.vistas.values():
            vista.grid_forget()
        
        # Mostrar la vista solicitada
        vista = self.vistas.get(nombre_vista)
        if vista:
            # Inicializar la vista con parámetros si es necesario
            vista.inicializar(*args, **kwargs)
            vista.grid(row=0, column=0, sticky="nsew")
        else:
            print(f"Error: Vista '{nombre_vista}' no encontrada")

if __name__ == "__main__":
    app = App()
    app.mainloop()
