import customtkinter as ctk
from datetime import datetime
import requests
from PIL import Image, ImageTk
from .base_vista import BaseView
from utils.estilos import aplicar_estilo, COLORES

class GestionListaView(BaseView):
    """Vista para gestionar la lista doblemente enlazada de vuelos"""
    
    def crear_widgets(self):
        # Frame principal
        self.frame_contenido = ctk.CTkFrame(self)
        self.frame_contenido.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        self.frame_contenido.grid_rowconfigure(2, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_contenido,
            text="Gestión de Lista de Vuelos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Panel de estadísticas y acciones
        self.crear_panel_superior()
        
        # Visualización de la lista
        self.crear_visualizacion_lista()
        
        # Panel inferior con botones de acción
        self.crear_panel_inferior()
    
    def crear_panel_superior(self):
        """Crea el panel superior con estadísticas y acciones rápidas"""
        # Frame para el panel superior
        self.frame_superior = ctk.CTkFrame(self.frame_contenido)
        self.frame_superior.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.frame_superior.grid_columnconfigure(0, weight=1)
        self.frame_superior.grid_columnconfigure(1, weight=1)
        
        # Panel de estadísticas
        self.frame_stats = ctk.CTkFrame(self.frame_superior)
        aplicar_estilo(self.frame_stats, "card_frame")
        self.frame_stats.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        self.label_stats_titulo = ctk.CTkLabel(
            self.frame_stats,
            text="Estadísticas de la Lista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_stats_titulo.pack(pady=(10, 5))
        
        self.label_tamanio = ctk.CTkLabel(
            self.frame_stats,
            text="Tamaño de la lista: ...",
            font=ctk.CTkFont(size=14)
        )
        self.label_tamanio.pack(anchor="w", padx=15, pady=(5, 0))
        
        self.label_primer_vuelo = ctk.CTkLabel(
            self.frame_stats,
            text="Primer vuelo: ...",
            font=ctk.CTkFont(size=14)
        )
        self.label_primer_vuelo.pack(anchor="w", padx=15, pady=(5, 0))
        
        self.label_ultimo_vuelo = ctk.CTkLabel(
            self.frame_stats,
            text="Último vuelo: ...",
            font=ctk.CTkFont(size=14)
        )
        self.label_ultimo_vuelo.pack(anchor="w", padx=15, pady=(5, 10))
        
        # Panel de acciones rápidas
        self.frame_acciones = ctk.CTkFrame(self.frame_superior)
        aplicar_estilo(self.frame_acciones, "card_frame")
        self.frame_acciones.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        self.label_acciones_titulo = ctk.CTkLabel(
            self.frame_acciones,
            text="Acciones Rápidas",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_acciones_titulo.pack(pady=(10, 5))
        
        # Frame para botones en fila
        self.frame_botones_acciones = ctk.CTkFrame(self.frame_acciones)
        self.frame_botones_acciones.pack(fill="x", padx=15, pady=(5, 10))
        
        # Botón para reordenar lista
        self.btn_reordenar = ctk.CTkButton(
            self.frame_botones_acciones,
            text="Reordenar Lista",
            command=self.reordenar_lista
        )
        aplicar_estilo(self.btn_reordenar, "button")
        self.btn_reordenar.grid(row=0, column=0, padx=5, pady=5)
        
        # Botón para refrescar
        self.btn_refrescar = ctk.CTkButton(
            self.frame_botones_acciones,
            text="Refrescar",
            command=self.cargar_datos
        )
        aplicar_estilo(self.btn_refrescar, "button")
        self.btn_refrescar.grid(row=0, column=1, padx=5, pady=5)
        
        # Botón para extraer el primer vuelo
        self.btn_extraer_primero = ctk.CTkButton(
            self.frame_botones_acciones,
            text="Extraer Primero",
            command=lambda: self.extraer_vuelo(0)
        )
        aplicar_estilo(self.btn_extraer_primero, "button")
        self.btn_extraer_primero.grid(row=1, column=0, padx=5, pady=5)
        
        # Botón para extraer el último vuelo
        self.btn_extraer_ultimo = ctk.CTkButton(
            self.frame_botones_acciones,
            text="Extraer Último",
            command=self.extraer_ultimo
        )
        aplicar_estilo(self.btn_extraer_ultimo, "button")
        self.btn_extraer_ultimo.grid(row=1, column=1, padx=5, pady=5)
    
    def crear_visualizacion_lista(self):
        """Crea la visualización gráfica de la lista enlazada"""
        # Frame para la visualización con scroll
        self.frame_lista = ctk.CTkScrollableFrame(self.frame_contenido)
        self.frame_lista.grid(row=2, column=0, sticky="nsew")
        self.frame_lista.grid_columnconfigure(0, weight=1)
        
        # Inicializar contenedor para nodos
        self.nodos_frames = []
    
    def crear_panel_inferior(self):
        """Crea el panel inferior con operaciones sobre la lista"""
        # Frame para el panel inferior
        self.frame_inferior = ctk.CTkFrame(self.frame_contenido)
        self.frame_inferior.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        self.frame_inferior.grid_columnconfigure(1, weight=1)
        
        # Label de título
        self.label_operaciones = ctk.CTkLabel(
            self.frame_inferior,
            text="Operaciones con la Lista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.label_operaciones.grid(row=0, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 15))
        
        # Frame para primera operación: Mover nodo
        self.frame_mover = ctk.CTkFrame(self.frame_inferior)
        self.frame_mover.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")
        
        self.label_mover = ctk.CTkLabel(
            self.frame_mover,
            text="Mover nodo entre posiciones",
            font=ctk.CTkFont(weight="bold")
        )
        self.label_mover.grid(row=0, column=0, columnspan=5, padx=10, pady=(10, 5), sticky="w")
        
        self.label_origen = ctk.CTkLabel(self.frame_mover, text="Origen:")
        self.label_origen.grid(row=1, column=0, padx=(10, 5), pady=(0, 10))
        
        self.entry_origen = ctk.CTkEntry(self.frame_mover, width=60)
        self.entry_origen.grid(row=1, column=1, padx=(0, 10), pady=(0, 10))
        self.entry_origen.insert(0, "0")
        
        self.label_destino = ctk.CTkLabel(self.frame_mover, text="Destino:")
        self.label_destino.grid(row=1, column=2, padx=(10, 5), pady=(0, 10))
        
        self.entry_destino = ctk.CTkEntry(self.frame_mover, width=60)
        self.entry_destino.grid(row=1, column=3, padx=(0, 10), pady=(0, 10))
        self.entry_destino.insert(0, "0")
        
        self.btn_mover = ctk.CTkButton(
            self.frame_mover,
            text="Mover",
            width=80,
            command=self.mover_nodo
        )
        aplicar_estilo(self.btn_mover, "button")
        self.btn_mover.grid(row=1, column=4, padx=(0, 10), pady=(0, 10))
        
        # Frame para segunda operación: Extraer nodo
        self.frame_extraer = ctk.CTkFrame(self.frame_inferior)
        self.frame_extraer.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="ew")
        
        self.label_extraer = ctk.CTkLabel(
            self.frame_extraer,
            text="Extraer nodo de posición",
            font=ctk.CTkFont(weight="bold")
        )
        self.label_extraer.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="w")
        
        self.label_posicion = ctk.CTkLabel(self.frame_extraer, text="Posición:")
        self.label_posicion.grid(row=1, column=0, padx=(10, 5), pady=(0, 10))
        
        self.entry_posicion = ctk.CTkEntry(self.frame_extraer, width=60)
        self.entry_posicion.grid(row=1, column=1, padx=(0, 10), pady=(0, 10))
        self.entry_posicion.insert(0, "0")
        
        self.btn_extraer = ctk.CTkButton(
            self.frame_extraer,
            text="Extraer",
            width=80,
            command=lambda: self.extraer_vuelo_posicion()
        )
        aplicar_estilo(self.btn_extraer, "button")
        self.btn_extraer.grid(row=1, column=2, padx=(0, 10), pady=(0, 10))
    
    def inicializar(self):
        """Inicializa la vista cargando los datos"""
        self.cargar_datos()
    
    def cargar_datos(self):
        """Carga los datos de la lista desde la API"""
        try:
            # Cargar datos de la lista
            lista_con_nodos = self.cliente_api.obtener_lista()
            
            # Actualizar estadísticas
            self.actualizar_estadisticas()
            
            # Limpiar visualización actual
            for nodo_frame in self.nodos_frames:
                nodo_frame.destroy()
            self.nodos_frames = []
            
            # Crear visualización para cada nodo
            self.visualizar_lista(lista_con_nodos)
            
        except Exception as e:
            self.manejar_error_api(e, "Error al cargar los datos de la lista")
    
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en el panel superior"""
        try:
            # Obtener tamaño de la lista
            tamanio = self.cliente_api.obtener_cantidad_nodos()
            self.label_tamanio.configure(text=f"Tamaño de la lista: {tamanio}")
            
            # Habilitar/deshabilitar botones según tamaño
            if tamanio > 0:
                self.btn_extraer_primero.configure(state="normal")
                self.btn_extraer_ultimo.configure(state="normal")
            else:
                self.btn_extraer_primero.configure(state="disabled")
                self.btn_extraer_ultimo.configure(state="disabled")
            
            # Obtener primer vuelo
            primer_vuelo = self.cliente_api.obtener_primer_vuelo()
            if primer_vuelo:
                self.label_primer_vuelo.configure(
                    text=f"Primer vuelo: {primer_vuelo.get('numero_vuelo')} ({primer_vuelo.get('origen')} → {primer_vuelo.get('destino')})"
                )
            else:
                self.logger.info("No hay primer vuelo disponible")
                self.label_primer_vuelo.configure(text="Primer vuelo: No hay vuelos en la lista")
            
            # Obtener último vuelo
            ultimo_vuelo = self.cliente_api.obtener_ultimo_vuelo()
            if ultimo_vuelo:
                self.label_ultimo_vuelo.configure(
                    text=f"Último vuelo: {ultimo_vuelo.get('numero_vuelo')} ({ultimo_vuelo.get('origen')} → {ultimo_vuelo.get('destino')})"
                )
            else:
                self.logger.info("No hay último vuelo disponible")
                self.label_ultimo_vuelo.configure(text="Último vuelo: No hay vuelos en la lista")
                
        except Exception as e:
            self.logger.error(f"Error al actualizar estadísticas: {str(e)}")
            self.manejar_error_api(e, "Error al actualizar estadísticas")
    
    def visualizar_lista(self, lista_con_nodos):
        """Crea una visualización gráfica de la lista enlazada"""
        # Obtener los nodos de la lista
        nodos = lista_con_nodos.get('nodos', [])
        
        # Si no hay nodos, mostrar mensaje
        if not nodos:
            frame_vacio = ctk.CTkFrame(self.frame_lista)
            aplicar_estilo(frame_vacio, "card_frame")
            frame_vacio.grid(row=0, column=0, sticky="ew", pady=10)
            
            label_vacio = ctk.CTkLabel(
                frame_vacio,
                text="La lista está vacía. Añada vuelos desde la lista de vuelos.",
                font=ctk.CTkFont(size=14),
                pady=20
            )
            label_vacio.pack()
            
            self.nodos_frames.append(frame_vacio)
            return
        
        # Crear un frame para cada nodo
        for i, nodo in enumerate(nodos):
            # Obtener el vuelo asociado al nodo
            vuelo = nodo.get('vuelo')
            
            # Crear frame para el nodo
            frame_nodo = ctk.CTkFrame(self.frame_lista)
            aplicar_estilo(frame_nodo, "card_frame")
            frame_nodo.grid(row=i, column=0, sticky="ew", pady=5)
            
            # Verificar si es un vuelo de emergencia para cambiar el color
            if vuelo.get('emergencia'):
                frame_nodo.configure(fg_color="#ffebee")  # Color rojo claro
            
            # Grid layout para el frame del nodo
            frame_nodo.grid_columnconfigure(1, weight=1)
            
            # Posición del nodo
            label_posicion = ctk.CTkLabel(
                frame_nodo,
                text=f"#{nodo.get('posicion')}",
                font=ctk.CTkFont(size=18, weight="bold"),
                width=40,
                height=40
            )
            label_posicion.grid(row=0, column=0, rowspan=2, padx=(10, 5), pady=10)
            
            # ID del vuelo
            label_id = ctk.CTkLabel(
                frame_nodo,
                text=f"ID: {vuelo.get('id')}",
                font=ctk.CTkFont(size=10),
                anchor="w"
            )
            label_id.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=(10, 0))
            
            # Información principal del vuelo
            label_info = ctk.CTkLabel(
                frame_nodo,
                text=f"Vuelo: {vuelo.get('numero_vuelo')} - {vuelo.get('origen')} → {vuelo.get('destino')}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            label_info.grid(row=1, column=1, sticky="w", padx=(0, 10), pady=(0, 5))
            
            # Detalles del vuelo
            hora_salida = datetime.fromisoformat(vuelo.get('hora_salida')).strftime('%d/%m/%Y %H:%M')
            hora_llegada = datetime.fromisoformat(vuelo.get('hora_llegada')).strftime('%d/%m/%Y %H:%M')
            
            label_detalles = ctk.CTkLabel(
                frame_nodo,
                text=f"Salida: {hora_salida} | Llegada: {hora_llegada} | Estado: {vuelo.get('estado', '').capitalize()} | Prioridad: {vuelo.get('prioridad')}",
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            label_detalles.grid(row=2, column=1, columnspan=2, sticky="w", padx=(0, 10), pady=(0, 10))
            
            # Indicador de emergencia
            if vuelo.get('emergencia'):
                label_emergencia = ctk.CTkLabel(
                    frame_nodo,
                    text="EMERGENCIA",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="red",
                    anchor="e"
                )
                label_emergencia.grid(row=0, column=2, padx=(0, 10), pady=(10, 0))
            
            # Botones de acción
            frame_botones = ctk.CTkFrame(frame_nodo)
            frame_botones.grid(row=1, column=2, padx=(0, 10), pady=(0, 5))
            
            btn_extraer = ctk.CTkButton(
                frame_botones,
                text="Extraer",
                width=80,
                command=lambda pos=nodo.get('posicion'): self.extraer_vuelo(pos)
            )
            aplicar_estilo(btn_extraer, "button")
            btn_extraer.grid(row=0, column=0, padx=5, pady=5)
            
            # Almacenar el frame para limpieza posterior
            self.nodos_frames.append(frame_nodo)
    
    def reordenar_lista(self):
        """Reordena la lista según prioridad y estado de emergencia"""
        try:
            self.cliente_api.reordenar_lista()
            self.mostrar_mensaje("Éxito", "Lista reordenada correctamente", "check")
            self.cargar_datos()
        except Exception as e:
            self.manejar_error_api(e, "Error al reordenar la lista")
    
    def extraer_vuelo(self, posicion):
        """Extrae un vuelo de la posición especificada"""
        try:
            # Confirmar la extracción
            if self.confirmar_accion("Confirmar extracción", 
                                    f"¿Desea extraer el vuelo en la posición {posicion}?\nEsta acción no se puede deshacer."):
                # Extraer el vuelo
                self.cliente_api.extraer_vuelo_de_posicion(posicion)
                self.mostrar_mensaje("Éxito", f"Vuelo extraído correctamente de la posición {posicion}", "check")
                self.cargar_datos()
        except Exception as e:
            self.manejar_error_api(e, "Error al extraer el vuelo")
    
    def extraer_ultimo(self):
        """Extrae el último vuelo de la lista"""
        try:
            # Obtener la cantidad de nodos
            tamanio = self.cliente_api.obtener_cantidad_nodos()
            if tamanio > 0:
                # Extraer el último vuelo (posición = tamaño - 1)
                self.extraer_vuelo(tamanio - 1)
        except Exception as e:
            self.manejar_error_api(e, "Error al extraer el último vuelo")
    
    def extraer_vuelo_posicion(self):
        """Extrae un vuelo de la posición ingresada por el usuario"""
        try:
            # Obtener la posición ingresada
            posicion_str = self.entry_posicion.get()
            try:
                posicion = int(posicion_str)
                self.extraer_vuelo(posicion)
            except ValueError:
                self.mostrar_mensaje("Error", "La posición debe ser un número entero", "cancel")
        except Exception as e:
            self.manejar_error_api(e, "Error al extraer el vuelo")
    
    def mover_nodo(self):
        """Mueve un nodo entre posiciones"""
        try:
            # Obtener las posiciones
            origen_str = self.entry_origen.get()
            destino_str = self.entry_destino.get()
            
            try:
                origen = int(origen_str)
                destino = int(destino_str)
                
                # Confirmar la operación
                if self.confirmar_accion("Confirmar movimiento", 
                                       f"¿Desea mover el nodo de la posición {origen} a la posición {destino}?"):
                    # Realizar movimiento
                    self.cliente_api.mover_nodo(origen, destino)
                    self.mostrar_mensaje("Éxito", f"Nodo movido correctamente de la posición {origen} a la posición {destino}", "check")
                    self.cargar_datos()
            except ValueError:
                self.mostrar_mensaje("Error", "Las posiciones deben ser números enteros", "cancel")
        except Exception as e:
            self.manejar_error_api(e, "Error al mover el nodo")
