import customtkinter as ctk
from datetime import datetime
import requests
from PIL import Image, ImageTk
from .base_vista import BaseView
from utils.estilos import aplicar_estilo, COLORES

class DashboardView(BaseView):
    """Vista principal del dashboard con resumen del sistema"""
    
    def crear_widgets(self):
        # Frame principal
        self.frame_contenido = ctk.CTkFrame(self)
        self.frame_contenido.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(1, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_contenido,
            text="Dashboard de Control de Aeropuerto",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Tarjetas de resumen
        self.crear_tarjetas_resumen()
        
        # Sección de próximos vuelos
        self.crear_seccion_vuelos()
        
        # Sección de acciones rápidas
        self.crear_acciones_rapidas()
        
        # Botón para actualizar dashboard
        self.btn_actualizar = ctk.CTkButton(
            self.frame_contenido,
            text="Actualizar Dashboard",
            command=self.actualizar_dashboard
        )
        aplicar_estilo(self.btn_actualizar, "button")
        self.btn_actualizar.grid(row=4, column=0, columnspan=2, pady=(20, 0), sticky="e")
    
    def crear_tarjetas_resumen(self):
        # Frame de tarjetas de resumen
        self.frame_tarjetas = ctk.CTkFrame(self.frame_contenido)
        self.frame_tarjetas.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        self.frame_tarjetas.grid_columnconfigure(0, weight=1)
        self.frame_tarjetas.grid_columnconfigure(1, weight=1)
        self.frame_tarjetas.grid_columnconfigure(2, weight=1)
        
        # Tarjeta 1: Total de vuelos
        self.tarjeta_total = ctk.CTkFrame(self.frame_tarjetas)
        aplicar_estilo(self.tarjeta_total, "card_frame")
        self.tarjeta_total.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.label_total_titulo = ctk.CTkLabel(
            self.tarjeta_total,
            text="Total de Vuelos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_total_titulo.pack(pady=(10, 5))
        
        self.label_total_valor = ctk.CTkLabel(
            self.tarjeta_total,
            text="...",
            font=ctk.CTkFont(size=28)
        )
        self.label_total_valor.pack(pady=(0, 10))
        
        # Tarjeta 2: Vuelos en lista
        self.tarjeta_lista = ctk.CTkFrame(self.frame_tarjetas)
        aplicar_estilo(self.tarjeta_lista, "card_frame")
        self.tarjeta_lista.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.label_lista_titulo = ctk.CTkLabel(
            self.tarjeta_lista,
            text="Vuelos en Lista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_lista_titulo.pack(pady=(10, 5))
        
        self.label_lista_valor = ctk.CTkLabel(
            self.tarjeta_lista,
            text="...",
            font=ctk.CTkFont(size=28)
        )
        self.label_lista_valor.pack(pady=(0, 10))
        
        # Tarjeta 3: Vuelos de emergencia
        self.tarjeta_emergencia = ctk.CTkFrame(self.frame_tarjetas)
        aplicar_estilo(self.tarjeta_emergencia, "card_frame")
        self.tarjeta_emergencia.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.label_emergencia_titulo = ctk.CTkLabel(
            self.tarjeta_emergencia,
            text="Vuelos de Emergencia",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORES["danger"]
        )
        self.label_emergencia_titulo.pack(pady=(10, 5))
        
        self.label_emergencia_valor = ctk.CTkLabel(
            self.tarjeta_emergencia,
            text="...",
            font=ctk.CTkFont(size=28),
            text_color=COLORES["danger"]
        )
        self.label_emergencia_valor.pack(pady=(0, 10))
    
    def crear_seccion_vuelos(self):
        # Frame de próximos vuelos
        self.frame_proximos = ctk.CTkFrame(self.frame_contenido)
        aplicar_estilo(self.frame_proximos, "card_frame")
        self.frame_proximos.grid(row=2, column=0, padx=(0, 10), pady=(0, 20), sticky="nsew")
        
        self.label_proximos = ctk.CTkLabel(
            self.frame_proximos,
            text="Próximo Vuelo en Lista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_proximos.pack(pady=(10, 5), padx=10)
        
        # Contenido del vuelo
        self.label_vuelo_info = ctk.CTkLabel(
            self.frame_proximos,
            text="No hay vuelos en la lista",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        self.label_vuelo_info.pack(pady=(0, 10), padx=15, anchor="w")
        
        self.label_vuelo_detalles = ctk.CTkLabel(
            self.frame_proximos,
            text="",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        self.label_vuelo_detalles.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Botón para ver siguiente vuelo
        self.btn_extraer = ctk.CTkButton(
            self.frame_proximos,
            text="Extraer Vuelo",
            command=self.extraer_primer_vuelo
        )
        aplicar_estilo(self.btn_extraer, "button")
        self.btn_extraer.pack(pady=(0, 10))
    
    def crear_acciones_rapidas(self):
        # Frame de acciones rápidas
        self.frame_acciones = ctk.CTkFrame(self.frame_contenido)
        aplicar_estilo(self.frame_acciones, "card_frame")
        self.frame_acciones.grid(row=2, column=1, padx=(10, 0), pady=(0, 20), sticky="nsew")
        
        self.label_acciones = ctk.CTkLabel(
            self.frame_acciones,
            text="Acciones Rápidas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_acciones.pack(pady=(10, 15), padx=10)
        
        # Botón para crear vuelo
        self.btn_crear_vuelo = ctk.CTkButton(
            self.frame_acciones,
            text="Crear Nuevo Vuelo",
            command=lambda: self.controller.mostrar_vista("detalle_vuelo", None)
        )
        aplicar_estilo(self.btn_crear_vuelo, "button")
        self.btn_crear_vuelo.pack(pady=(0, 10), padx=20, fill="x")
        
        # Botón para ver todos los vuelos
        self.btn_ver_vuelos = ctk.CTkButton(
            self.frame_acciones,
            text="Ver Todos los Vuelos",
            command=lambda: self.controller.mostrar_vista("lista_vuelos")
        )
        aplicar_estilo(self.btn_ver_vuelos, "button")
        self.btn_ver_vuelos.pack(pady=(0, 10), padx=20, fill="x")
        
        # Botón para gestionar lista
        self.btn_gestionar_lista = ctk.CTkButton(
            self.frame_acciones,
            text="Gestionar Lista de Vuelos",
            command=lambda: self.controller.mostrar_vista("gestion_lista")
        )
        aplicar_estilo(self.btn_gestionar_lista, "button")
        self.btn_gestionar_lista.pack(pady=(0, 10), padx=20, fill="x")
        
        # Botón para reordenar lista
        self.btn_reordenar = ctk.CTkButton(
            self.frame_acciones,
            text="Reordenar Lista por Prioridad",
            command=self.reordenar_lista
        )
        aplicar_estilo(self.btn_reordenar, "button")
        self.btn_reordenar.pack(pady=(0, 10), padx=20, fill="x")
    
    def inicializar(self):
        """Inicializa el dashboard cargando los datos"""
        self.actualizar_dashboard()
    
    def actualizar_dashboard(self):
        """Actualiza todos los datos del dashboard"""
        try:
            # Actualizar contadores
            self.actualizar_contadores()
            
            # Actualizar próximo vuelo
            self.actualizar_proximo_vuelo()
            
        except Exception as e:
            self.manejar_error_api(e, "Error al cargar los datos del dashboard")
    
    def actualizar_contadores(self):
        """Actualiza los contadores de las tarjetas resumen"""
        try:
            # Total de vuelos
            vuelos = self.cliente_api.obtener_vuelos()
            self.label_total_valor.configure(text=str(len(vuelos)))
            
            # Contar vuelos de emergencia
            emergencias = sum(1 for v in vuelos if v.get('emergencia', False))
            self.label_emergencia_valor.configure(text=str(emergencias))
            
            # Vuelos en lista
            try:
                cantidad_lista = self.cliente_api.obtener_cantidad_nodos()
                self.label_lista_valor.configure(text=str(cantidad_lista))
            except:
                self.label_lista_valor.configure(text="0")
                
        except Exception as e:
            self.manejar_error_api(e, "Error al actualizar contadores")
    
    def actualizar_proximo_vuelo(self):
        """Actualiza la información del próximo vuelo en la lista"""
        try:
            primer_vuelo = self.cliente_api.obtener_primer_vuelo()
            if primer_vuelo:
                # Formatear la información del vuelo
                numero_vuelo = primer_vuelo.get('numero_vuelo', 'N/A')
                origen = primer_vuelo.get('origen', 'N/A')
                destino = primer_vuelo.get('destino', 'N/A')
                estado = primer_vuelo.get('estado', 'N/A').capitalize()
                emergencia = "SÍ" if primer_vuelo.get('emergencia', False) else "NO"
                
                # Formatear fechas
                hora_salida = datetime.fromisoformat(primer_vuelo.get('hora_salida')).strftime('%d/%m/%Y %H:%M')
                hora_llegada = datetime.fromisoformat(primer_vuelo.get('hora_llegada')).strftime('%d/%m/%Y %H:%M')
                
                # Actualizar información
                self.label_vuelo_info.configure(
                    text=f"Vuelo: {numero_vuelo} - {origen} → {destino}"
                )
                self.label_vuelo_detalles.configure(
                    text=f"Salida: {hora_salida}\n"
                         f"Llegada: {hora_llegada}\n"
                         f"Estado: {estado}\n"
                         f"Emergencia: {emergencia}\n"
                         f"Prioridad: {primer_vuelo.get('prioridad', 0)}"
                )
                
                # Habilitar botón de extraer
                self.btn_extraer.configure(state="normal")
            else:
                self.logger.info("No hay próximo vuelo disponible en la lista")
                self.label_vuelo_info.configure(text="No hay vuelos en la lista")
                self.label_vuelo_detalles.configure(text="")
                self.btn_extraer.configure(state="disabled")
                
        except Exception as e:
            self.logger.error(f"Error al actualizar próximo vuelo: {str(e)}")
            self.label_vuelo_info.configure(text="Error al cargar datos")
            self.label_vuelo_detalles.configure(text="")
            self.btn_extraer.configure(state="disabled")
    
    def extraer_primer_vuelo(self):
        """Extrae el primer vuelo de la lista"""
        try:
            # Confirmar la extracción
            if self.confirmar_accion("Confirmar extracción", "¿Desea extraer el primer vuelo de la lista?"):
                # Extraer el vuelo
                self.cliente_api.extraer_vuelo_de_posicion(0)
                self.mostrar_mensaje("Éxito", "Vuelo extraído correctamente", "check")
                
                # Actualizar dashboard
                self.actualizar_dashboard()
        except Exception as e:
            self.manejar_error_api(e, "Error al extraer el vuelo")
    
    def reordenar_lista(self):
        """Reordena la lista por prioridad"""
        try:
            self.cliente_api.reordenar_lista()
            self.mostrar_mensaje("Éxito", "Lista reordenada correctamente", "check")
            
            # Actualizar dashboard
            self.actualizar_dashboard()
        except Exception as e:
            self.manejar_error_api(e, "Error al reordenar la lista")
