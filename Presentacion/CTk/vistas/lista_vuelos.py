import customtkinter as ctk
from datetime import datetime
import requests
from .base_vista import BaseView
from utils.estilos import aplicar_estilo, COLORES

class ListaVuelosView(BaseView):
    """Vista para mostrar todos los vuelos registrados"""
    
    def crear_widgets(self):
        # Frame principal
        self.frame_contenido = ctk.CTkFrame(self)
        self.frame_contenido.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        self.frame_contenido.grid_rowconfigure(1, weight=1)
        
        # Header
        self.crear_header()
        
        # Tabla de vuelos
        self.crear_tabla()
        
        # Footer con botones de acción
        self.crear_footer()
        
        # Inicializar selección
        self.seleccion_actual = None
    
    def crear_header(self):
        """Crea el encabezado con título y buscador"""
        # Frame del header
        self.frame_header = ctk.CTkFrame(self.frame_contenido)
        self.frame_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.frame_header.grid_columnconfigure(1, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_header,
            text="Lista de Vuelos",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Buscador
        self.entry_buscar = ctk.CTkEntry(
            self.frame_header,
            placeholder_text="Buscar por número de vuelo, origen o destino..."
        )
        aplicar_estilo(self.entry_buscar, "entry")
        self.entry_buscar.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Botón de búsqueda
        self.btn_buscar = ctk.CTkButton(
            self.frame_header,
            text="Buscar",
            width=100,
            command=self.buscar_vuelos
        )
        aplicar_estilo(self.btn_buscar, "button")
        self.btn_buscar.grid(row=0, column=2)
        
        # Botón de agregar
        self.btn_agregar = ctk.CTkButton(
            self.frame_header,
            text="+ Nuevo Vuelo",
            width=150,
            command=lambda: self.controller.mostrar_vista("detalle_vuelo", None)
        )
        aplicar_estilo(self.btn_agregar, "success_button")
        self.btn_agregar.grid(row=0, column=3, padx=(10, 0))
    
    def crear_tabla(self):
        """Crea la tabla de vuelos"""
        # Frame para la tabla
        self.frame_tabla = ctk.CTkScrollableFrame(self.frame_contenido)
        self.frame_tabla.grid(row=1, column=0, sticky="nsew")
        self.frame_tabla.grid_columnconfigure(0, weight=1)
        
        # Cabecera de la tabla
        self.crear_cabecera_tabla()
        
        # El contenido de la tabla se cargará dinámicamente
        self.filas_tabla = []
    
    def crear_cabecera_tabla(self):
        """Crea la cabecera de la tabla de vuelos"""
        # Frame para la cabecera
        self.frame_cabecera = ctk.CTkFrame(self.frame_tabla)
        aplicar_estilo(self.frame_cabecera, "card_frame")
        self.frame_cabecera.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Configurar columnas
        columnas = ["Vuelo", "Origen", "Destino", "Salida", "Llegada", "Estado", "Prioridad", "Emergencia"]
        pesos = [1, 1, 1, 1, 1, 1, 1, 1]
        
        for i, (col, peso) in enumerate(zip(columnas, pesos)):
            self.frame_cabecera.grid_columnconfigure(i, weight=peso)
            ctk.CTkLabel(
                self.frame_cabecera,
                text=col,
                font=ctk.CTkFont(weight="bold"),
                padx=10, pady=10
            ).grid(row=0, column=i, sticky="ew")
    
    def crear_footer(self):
        """Crea el pie de página con botones de acción"""
        # Frame para footer
        self.frame_footer = ctk.CTkFrame(self.frame_contenido)
        self.frame_footer.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.frame_footer.grid_columnconfigure(0, weight=1)
        
        # Frame para botones
        self.frame_botones = ctk.CTkFrame(self.frame_footer)
        self.frame_botones.grid(row=0, column=0, pady=10)
        
        # Botones de acción
        self.btn_editar = ctk.CTkButton(
            self.frame_botones,
            text="Editar Vuelo",
            width=150,
            state="disabled",
            command=self.editar_vuelo_seleccionado
        )
        aplicar_estilo(self.btn_editar, "button")
        self.btn_editar.grid(row=0, column=0, padx=5)
        
        self.btn_eliminar = ctk.CTkButton(
            self.frame_botones,
            text="Eliminar Vuelo",
            width=150,
            state="disabled",
            command=self.eliminar_vuelo_seleccionado
        )
        aplicar_estilo(self.btn_eliminar, "danger_button")
        self.btn_eliminar.grid(row=0, column=1, padx=5)
        
        self.btn_agregar_lista = ctk.CTkButton(
            self.frame_botones,
            text="Agregar a Lista",
            width=150,
            state="disabled",
            command=self.agregar_a_lista
        )
        aplicar_estilo(self.btn_agregar_lista, "button")
        self.btn_agregar_lista.grid(row=0, column=2, padx=5)
        
        # Frame de estadísticas
        self.frame_stats = ctk.CTkFrame(self.frame_footer)
        self.frame_stats.grid(row=0, column=1, pady=10, padx=10)
        
        self.label_stats = ctk.CTkLabel(
            self.frame_stats,
            text="Total de vuelos: 0",
            font=ctk.CTkFont(size=12)
        )
        self.label_stats.pack(padx=10, pady=5)
        
        # Botón de actualizar
        self.btn_actualizar = ctk.CTkButton(
            self.frame_footer,
            text="↻ Actualizar",
            width=100,
            command=self.cargar_vuelos
        )
        aplicar_estilo(self.btn_actualizar, "button")
        self.btn_actualizar.grid(row=0, column=2, pady=10, padx=10)
    
    def inicializar(self):
        """Inicializa la vista cargando los datos"""
        self.cargar_vuelos()
    
    def cargar_vuelos(self):
        """Carga los vuelos desde la API"""
        try:
            # Limpiar tabla existente
            for fila in self.filas_tabla:
                fila.destroy()
            self.filas_tabla = []
            
            # Obtener vuelos
            vuelos = self.cliente_api.obtener_vuelos()
            
            # Actualizar estadísticas
            self.label_stats.configure(text=f"Total de vuelos: {len(vuelos)}")
            
            # Llenar la tabla
            for i, vuelo in enumerate(vuelos):
                self.agregar_fila_vuelo(i + 1, vuelo)
                
            # Desactivar botones
            self.seleccion_actual = None
            self.btn_editar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.btn_agregar_lista.configure(state="disabled")
            
        except Exception as e:
            self.manejar_error_api(e, "Error al cargar los vuelos")
    
    def agregar_fila_vuelo(self, indice, vuelo):
        """Agrega una fila a la tabla con los datos del vuelo"""
        # Crear frame para la fila
        fila = ctk.CTkFrame(self.frame_tabla)
        aplicar_estilo(fila, "card_frame")
        fila.grid(row=indice, column=0, sticky="ew", pady=2)
        
        # Almacenar ID del vuelo en el frame
        fila.vuelo_id = vuelo.get('id')
        
        # Configurar columnas
        for i in range(8):
            fila.grid_columnconfigure(i, weight=1)
        
        # Formatear fechas
        hora_salida = datetime.fromisoformat(vuelo.get('hora_salida')).strftime('%d/%m/%Y\n%H:%M')
        hora_llegada = datetime.fromisoformat(vuelo.get('hora_llegada')).strftime('%d/%m/%Y\n%H:%M')
        
        # Determinar color para indicar estado/emergencia
        color_bg = None
        if vuelo.get('emergencia'):
            color_bg = "#ffebee"  # Rojo claro para emergencias
        elif vuelo.get('estado') == 'retrasado':
            color_bg = "#fff8e1"  # Amarillo claro para retrasados
        elif vuelo.get('estado') == 'cancelado':
            color_bg = "#f5f5f5"  # Gris claro para cancelados
        
        # Aplicar color de fondo si es necesario
        if color_bg:
            fila.configure(fg_color=color_bg)
        
        # Texto en negrita para vuelos de emergencia
        font_weight = "bold" if vuelo.get('emergencia') else "normal"
        
        # Agregar datos a columnas
        datos = [
            vuelo.get('numero_vuelo', ''),
            vuelo.get('origen', ''),
            vuelo.get('destino', ''),
            hora_salida,
            hora_llegada,
            vuelo.get('estado', '').capitalize(),
            str(vuelo.get('prioridad', 0)),
            "SÍ" if vuelo.get('emergencia') else "NO"
        ]
        
        for i, dato in enumerate(datos):
            label = ctk.CTkLabel(
                fila,
                text=dato,
                font=ctk.CTkFont(weight=font_weight),
                padx=10, pady=10
            )
            label.grid(row=0, column=i, sticky="ew")
        
        # Eventos clic para selección - Corregir el uso de lambda para preservar el valor de fila
        for widget in fila.winfo_children():
            widget.bind("<Button-1>", lambda e, f=fila: self.seleccionar_fila(f))
        fila.bind("<Button-1>", lambda e, f=fila: self.seleccionar_fila(f))
        
        # Almacenar la fila
        self.filas_tabla.append(fila)
    
    def seleccionar_fila(self, fila):
        """Maneja la selección de una fila"""
        # Desmarcar fila anterior
        if self.seleccion_actual:
            aplicar_estilo(self.seleccion_actual, "card_frame")
            
            # Restaurar el color si era un vuelo especial
            vuelo_id = getattr(self.seleccion_actual, 'vuelo_id', None)
            if vuelo_id:
                for v in self.cliente_api.obtener_vuelos():
                    if v.get('id') == vuelo_id:
                        if v.get('emergencia'):
                            self.seleccion_actual.configure(fg_color="#ffebee")
                        elif v.get('estado') == 'retrasado':
                            self.seleccion_actual.configure(fg_color="#fff8e1")
                        elif v.get('estado') == 'cancelado':
                            self.seleccion_actual.configure(fg_color="#f5f5f5")
                        break
        
        # Marcar nueva fila
        fila.configure(border_width=2, border_color=COLORES["primary"])
        self.seleccion_actual = fila
        
        # Mostrar la ID del vuelo seleccionado en el log
        self.logger.debug(f"Seleccionado vuelo con ID: {fila.vuelo_id}")
        
        # Habilitar botones - asegurarnos de que existan antes de configurarlos
        if hasattr(self, 'btn_editar'):
            self.btn_editar.configure(state="normal")
        if hasattr(self, 'btn_eliminar'):
            self.btn_eliminar.configure(state="normal")
        if hasattr(self, 'btn_agregar_lista'):
            self.btn_agregar_lista.configure(state="normal")
    
    def buscar_vuelos(self):
        """Filtra vuelos según el texto de búsqueda"""
        try:
            texto_busqueda = self.entry_buscar.get().lower()
            
            # Si no hay texto, mostrar todos
            if not texto_busqueda:
                self.cargar_vuelos()
                return
            
            # Obtener todos los vuelos para filtrarlos
            vuelos = self.cliente_api.obtener_vuelos()
            
            # Filtrar según criterios
            vuelos_filtrados = []
            for vuelo in vuelos:
                if (texto_busqueda in vuelo.get('numero_vuelo', '').lower() or
                    texto_busqueda in vuelo.get('origen', '').lower() or
                    texto_busqueda in vuelo.get('destino', '').lower()):
                    vuelos_filtrados.append(vuelo)
            
            # Limpiar tabla
            for fila in self.filas_tabla:
                fila.destroy()
            self.filas_tabla = []
            
            # Actualizar estadísticas
            self.label_stats.configure(text=f"Resultados: {len(vuelos_filtrados)} de {len(vuelos)}")
            
            # Llenar tabla filtrada
            for i, vuelo in enumerate(vuelos_filtrados):
                self.agregar_fila_vuelo(i + 1, vuelo)
            
            # Desactivar botones
            self.seleccion_actual = None
            self.btn_editar.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
            self.btn_agregar_lista.configure(state="disabled")
            
        except Exception as e:
            self.manejar_error_api(e, "Error al buscar vuelos")
    
    def editar_vuelo_seleccionado(self):
        """Abre la vista de detalle para editar el vuelo seleccionado"""
        if self.seleccion_actual and hasattr(self.seleccion_actual, 'vuelo_id'):
            vuelo_id = self.seleccion_actual.vuelo_id
            self.logger.info(f"Iniciando edición de vuelo con ID: {vuelo_id}")
            
            try:
                # Verificar si el vuelo está en la lista
                lista = self.cliente_api.obtener_lista()
                for nodo in lista.get('nodos', []):
                    if nodo.get('vuelo', {}).get('id') == vuelo_id:
                        # Mostrar advertencia pero permitir edición con precaución
                        self.logger.warning(f"Editando vuelo ID {vuelo_id} que está actualmente en la lista")
                        if self.confirmar_accion(
                            "Precaución", 
                            "Este vuelo está actualmente en la lista de programación.\n"
                            "Los cambios que realice pueden afectar el orden de la lista.\n"
                            "¿Desea continuar con la edición?"
                        ):
                            self.controller.mostrar_vista("detalle_vuelo", vuelo_id)
                        return
            except Exception as e:
                self.logger.error(f"Error al verificar si el vuelo está en la lista: {str(e)}")
                # Continuar con la edición aunque no podamos verificar la lista
            
            # Si llegamos aquí, el vuelo no está en la lista o hubo un error al verificar
            self.controller.mostrar_vista("detalle_vuelo", vuelo_id)
        else:
            self.logger.warning("Intento de editar un vuelo sin selección")
            self.mostrar_mensaje("Aviso", "Por favor, seleccione un vuelo para editar", "warning")
    
    def eliminar_vuelo_seleccionado(self):
        """Elimina el vuelo seleccionado"""
        if self.seleccion_actual and hasattr(self.seleccion_actual, 'vuelo_id'):
            try:
                vuelo_id = self.seleccion_actual.vuelo_id
                
                # Pedir confirmación
                try:
                    vuelo_info = self.cliente_api.obtener_vuelo(vuelo_id)
                    mensaje_confirmacion = (
                        f"¿Está seguro de eliminar este vuelo (ID: {vuelo_id})?\n"
                        f"Vuelo: {vuelo_info.get('numero_vuelo')}?\n"
                        f"Origen: {vuelo_info.get('origen')} - Destino: {vuelo_info.get('destino')}\n\n"
                        "Esta acción no se puede deshacer."
                    )
                except:
                    mensaje_confirmacion = (
                        f"¿Está seguro de eliminar este vuelo (ID: {vuelo_id})?\n"
                        "Esta acción no se puede deshacer."
                    )
                
                if self.confirmar_accion("Confirmar eliminación", mensaje_confirmacion):
                    # Eliminar vuelo
                    self.cliente_api.eliminar_vuelo(vuelo_id)
                    
                    # Mostrar mensaje y actualizar
                    self.mostrar_mensaje("Éxito", "Vuelo eliminado correctamente", "check")
                    self.cargar_vuelos()
            except Exception as e:
                self.manejar_error_api(e, "Error al eliminar el vuelo")
        else:
            self.mostrar_mensaje("Aviso", "Por favor, seleccione un vuelo para eliminar", "warning")
    
    def agregar_a_lista(self):
        """Abre el diálogo para agregar el vuelo a la lista"""
        if self.seleccion_actual and hasattr(self.seleccion_actual, 'vuelo_id'):
            vuelo_id = self.seleccion_actual.vuelo_id
            
            # Verificar si el vuelo ya está en la lista
            try:
                lista = self.cliente_api.obtener_lista()
                for nodo in lista.get('nodos', []):
                    if nodo.get('vuelo', {}).get('id') == vuelo_id:
                        self.mostrar_mensaje("Aviso", 
                            "Este vuelo ya está en la lista de programación.",
                            "warning")
                        return
            except Exception as e:
                self.logger.error(f"Error al verificar si el vuelo está en la lista: {str(e)}")
            
            # Mostrar el diálogo para agregar el vuelo
            self.mostrar_dialog_agregar_lista(vuelo_id)
        else:
            self.mostrar_mensaje("Aviso", "Por favor, seleccione un vuelo para agregar a la lista", "warning")
    
    def mostrar_dialog_agregar_lista(self, vuelo_id):
        """Muestra un diálogo para seleccionar cómo agregar el vuelo a la lista"""
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Agregar a Lista")
        dialog.geometry("400x350")  # Un poco más alto para dar espacio
        dialog.transient(self)
        dialog.grab_set()
        
        # Hacer la ventana modal
        dialog.focus_set()
        
        # Configurar layout
        dialog.grid_columnconfigure(0, weight=1)
        
        try:
            # Obtener información del vuelo para mostrarla en el diálogo
            vuelo_info = self.cliente_api.obtener_vuelo(vuelo_id)
            info_text = (
                f"Vuelo: {vuelo_info.get('numero_vuelo')}\n"
                f"Origen: {vuelo_info.get('origen')} - Destino: {vuelo_info.get('destino')}\n"
                f"Prioridad: {vuelo_info.get('prioridad')}\n"
                f"Emergencia: {'Sí' if vuelo_info.get('emergencia') else 'No'}"
            )
        except:
            info_text = f"Vuelo ID: {vuelo_id}"
        
        # Título
        titulo = ctk.CTkLabel(
            dialog,
            text="Agregar Vuelo a Lista",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        titulo.grid(row=0, column=0, padx=20, pady=(20, 5))
        
        # Información del vuelo
        info_label = ctk.CTkLabel(
            dialog,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        
        # Descripción
        descripcion = ctk.CTkLabel(
            dialog,
            text="Seleccione cómo desea agregar el vuelo a la lista:",
            font=ctk.CTkFont(size=12)
        )
        descripcion.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        # Frame de opciones
        frame_opciones = ctk.CTkFrame(dialog)
        frame_opciones.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        frame_opciones.grid_columnconfigure(0, weight=1)
        
        # Opción 1: Al frente
        btn_frente = ctk.CTkButton(
            frame_opciones,
            text="Agregar al Frente",
            command=lambda: self.agregar_vuelo_lista(vuelo_id, "frente", dialog)
        )
        aplicar_estilo(btn_frente, "button")
        btn_frente.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Opción 2: Al final
        btn_final = ctk.CTkButton(
            frame_opciones,
            text="Agregar al Final",
            command=lambda: self.agregar_vuelo_lista(vuelo_id, "final", dialog)
        )
        aplicar_estilo(btn_final, "button")
        btn_final.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Opción 3: Por prioridad
        btn_prioridad = ctk.CTkButton(
            frame_opciones,
            text="Ordenar por Prioridad",
            command=lambda: self.agregar_vuelo_lista(vuelo_id, "prioridad", dialog)
        )
        aplicar_estilo(btn_prioridad, "button")
        btn_prioridad.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Opción 4: En posición específica
        frame_posicion = ctk.CTkFrame(frame_opciones)
        frame_posicion.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        frame_posicion.grid_columnconfigure(1, weight=1)
        
        label_posicion = ctk.CTkLabel(frame_posicion, text="Posición:")
        label_posicion.grid(row=0, column=0, padx=(5, 10))
        
        entry_posicion = ctk.CTkEntry(frame_posicion)
        entry_posicion.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        entry_posicion.insert(0, "0")
        
        btn_posicion = ctk.CTkButton(
            frame_posicion,
            text="Agregar",
            width=80,
            command=lambda: self.agregar_vuelo_lista_posicion(vuelo_id, entry_posicion.get(), dialog)
        )
        aplicar_estilo(btn_posicion, "button")
        btn_posicion.grid(row=0, column=2, padx=(5, 5))
        
        # Botón de cancelar
        btn_cancelar = ctk.CTkButton(
            dialog,
            text="Cancelar",
            command=dialog.destroy
        )
        aplicar_estilo(btn_cancelar, "danger_button")
        btn_cancelar.grid(row=4, column=0, padx=20, pady=20)
    
    def agregar_vuelo_lista(self, vuelo_id, metodo, dialog=None):
        """Agrega un vuelo a la lista según el método seleccionado"""
        try:
            if metodo == "frente":
                self.cliente_api.insertar_vuelo_al_frente(vuelo_id)
                mensaje = "Vuelo agregado al frente de la lista"
            elif metodo == "final":
                self.cliente_api.insertar_vuelo_al_final(vuelo_id)
                mensaje = "Vuelo agregado al final de la lista"
            elif metodo == "prioridad":
                self.cliente_api.insertar_vuelo_ordenado(vuelo_id)
                mensaje = "Vuelo agregado a la lista ordenado por prioridad"
            
            if dialog:
                dialog.destroy()
            
            self.mostrar_mensaje("Éxito", mensaje, "check")
        
        except Exception as e:
            if dialog:
                dialog.destroy()
            self.manejar_error_api(e, "Error al agregar el vuelo a la lista")
    
    def agregar_vuelo_lista_posicion(self, vuelo_id, posicion_str, dialog=None):
        """Agrega un vuelo en una posición específica"""
        try:
            # Validar posición
            try:
                posicion = int(posicion_str)
            except ValueError:
                self.mostrar_mensaje("Error", "La posición debe ser un número entero", "cancel")
                return
            
            # Agregar a posición
            self.cliente_api.insertar_vuelo_ordenado(vuelo_id, posicion)
            
            # Cerrar diálogo si existe
            if dialog:
                dialog.destroy()
                
            # Mostrar mensaje de éxito
            self.mostrar_mensaje("Éxito", f"Vuelo agregado en la posición {posicion}", "check")
            
        except Exception as e:
            if dialog:
                dialog.destroy()
            self.manejar_error_api(e, f"Error al agregar el vuelo a la lista")
