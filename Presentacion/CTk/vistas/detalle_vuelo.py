import customtkinter as ctk
from datetime import datetime, timedelta  # Fixed import to include timedelta
import requests
from .base_vista import BaseView
from utils.estilos import aplicar_estilo, COLORES
from utils.validaciones import (
    validar_texto_no_vacio,
    validar_fecha_hora,
    validar_prioridad,
    validar_estado_vuelo,
    convertir_a_fecha_hora
)

class DetalleVueloView(BaseView):
    """Vista para crear y editar vuelos"""
    
    def crear_widgets(self):
        # Frame principal
        self.frame_contenido = ctk.CTkFrame(self)
        self.frame_contenido.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.frame_contenido.grid_columnconfigure(0, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self.frame_contenido,
            text="Nuevo Vuelo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.label_titulo.grid(row=0, column=0, pady=(0, 20), sticky="w")
        
        # Formulario
        self.crear_formulario()
        
        # Botones de acción
        self.crear_botones()
        
        # Inicializar variables
        self.vuelo_id = None
        self.modo_edicion = False
    
    def crear_formulario(self):
        """Crea el formulario para los datos del vuelo"""
        # Frame para el formulario con 2 columnas
        self.frame_form = ctk.CTkFrame(self.frame_contenido)
        self.frame_form.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.frame_form.grid_columnconfigure(0, weight=1)
        self.frame_form.grid_columnconfigure(1, weight=1)
        
        # Crear los campos del formulario
        
        # COLUMNA 1
        # Número de vuelo
        self.label_numero = ctk.CTkLabel(self.frame_form, text="Número de Vuelo:")
        self.label_numero.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.entry_numero = ctk.CTkEntry(self.frame_form, placeholder_text="Ejemplo: AA123")
        aplicar_estilo(self.entry_numero, "entry")
        self.entry_numero.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Origen
        self.label_origen = ctk.CTkLabel(self.frame_form, text="Origen:")
        self.label_origen.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.entry_origen = ctk.CTkEntry(self.frame_form, placeholder_text="Ciudad o aeropuerto de origen")
        aplicar_estilo(self.entry_origen, "entry")
        self.entry_origen.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Destino
        self.label_destino = ctk.CTkLabel(self.frame_form, text="Destino:")
        self.label_destino.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.entry_destino = ctk.CTkEntry(self.frame_form, placeholder_text="Ciudad o aeropuerto de destino")
        aplicar_estilo(self.entry_destino, "entry")
        self.entry_destino.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Estado
        self.label_estado = ctk.CTkLabel(self.frame_form, text="Estado del Vuelo:")
        self.label_estado.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.combobox_estado = ctk.CTkComboBox(
            self.frame_form,
            values=["programado", "retrasado", "cancelado"]
        )
        self.combobox_estado.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 15))
        self.combobox_estado.set("programado")
        
        # COLUMNA 2
        # Hora de salida
        self.label_hora_salida = ctk.CTkLabel(self.frame_form, text="Hora de Salida:")
        self.label_hora_salida.grid(row=0, column=1, sticky="w", padx=20, pady=(15, 5))
        
        self.entry_hora_salida = ctk.CTkEntry(self.frame_form, placeholder_text="YYYY-MM-DD HH:MM")
        aplicar_estilo(self.entry_hora_salida, "entry")
        self.entry_hora_salida.grid(row=1, column=1, sticky="ew", padx=20, pady=(0, 15))
        self.entry_hora_salida.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        # Hora de llegada
        self.label_hora_llegada = ctk.CTkLabel(self.frame_form, text="Hora de Llegada:")
        self.label_hora_llegada.grid(row=2, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.entry_hora_llegada = ctk.CTkEntry(self.frame_form, placeholder_text="YYYY-MM-DD HH:MM")
        aplicar_estilo(self.entry_hora_llegada, "entry")
        self.entry_hora_llegada.grid(row=3, column=1, sticky="ew", padx=20, pady=(0, 15))
        # Por defecto, 2 horas después de la salida
        llegada_default = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")  # Fixed: using timedelta directly
        self.entry_hora_llegada.insert(0, llegada_default)
        
        # Prioridad
        self.label_prioridad = ctk.CTkLabel(self.frame_form, text="Prioridad (0-100):")
        self.label_prioridad.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.slider_prioridad = ctk.CTkSlider(
            self.frame_form,
            from_=0,
            to=100,
            number_of_steps=100
        )
        self.slider_prioridad.grid(row=5, column=1, sticky="ew", padx=20, pady=(0, 5))
        self.slider_prioridad.set(50)  # Valor predeterminado
        
        self.label_valor_prioridad = ctk.CTkLabel(self.frame_form, text="50")
        self.label_valor_prioridad.grid(row=5, column=1, sticky="e", padx=(0, 20), pady=(0, 5))
        
        # Actualizar el valor mostrado cuando se mueve el slider
        self.slider_prioridad.configure(command=self.actualizar_valor_prioridad)
        
        # Emergencia
        self.label_emergencia = ctk.CTkLabel(self.frame_form, text="Emergencia:")
        self.label_emergencia.grid(row=6, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.switch_emergencia = ctk.CTkSwitch(
            self.frame_form, 
            text="Es emergencia",
            onvalue=True,
            offvalue=False
        )
        self.switch_emergencia.grid(row=7, column=1, sticky="w", padx=20, pady=(0, 15))
        
        # Frame para mensajes de error/validación
        self.frame_mensajes = ctk.CTkFrame(self.frame_contenido)
        self.frame_mensajes.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        self.frame_mensajes.grid_columnconfigure(0, weight=1)
        
        self.label_error = ctk.CTkLabel(
            self.frame_mensajes,
            text="",
            text_color=COLORES["danger"]
        )
        self.label_error.grid(row=0, column=0, padx=20, pady=10)
        self.frame_mensajes.grid_forget()  # Ocultar inicialmente
    
    def crear_botones(self):
        """Crea los botones de acción"""
        self.frame_botones = ctk.CTkFrame(self.frame_contenido)
        self.frame_botones.grid(row=3, column=0, sticky="ew")
        self.frame_botones.grid_columnconfigure(0, weight=1)
        
        # Botón de guardar
        self.btn_guardar = ctk.CTkButton(
            self.frame_botones,
            text="Guardar Vuelo",
            width=150,
            command=self.guardar_vuelo
        )
        aplicar_estilo(self.btn_guardar, "success_button")
        self.btn_guardar.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="e")
        
        # Botón de cancelar
        self.btn_cancelar = ctk.CTkButton(
            self.frame_botones,
            text="Cancelar",
            width=150,
            command=self.cancelar
        )
        aplicar_estilo(self.btn_cancelar, "danger_button")
        self.btn_cancelar.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="w")
    
    def inicializar(self, vuelo_id=None):
        """Inicializa la vista para crear un nuevo vuelo o editar uno existente"""
        self.vuelo_id = vuelo_id
        self.modo_edicion = vuelo_id is not None
        
        # Actualizar título según modo
        if self.modo_edicion:
            self.label_titulo.configure(text="Editar Vuelo")
            self.cargar_datos_vuelo(vuelo_id)
        else:
            self.label_titulo.configure(text="Nuevo Vuelo")
            self.limpiar_formulario()
        
        # Ocultar mensajes de error
        self.frame_mensajes.grid_forget()
    
    def actualizar_valor_prioridad(self, value):
        """Actualiza el texto que muestra el valor actual del slider"""
        self.label_valor_prioridad.configure(text=str(int(value)))
    
    def cargar_datos_vuelo(self, vuelo_id):
        """Carga los datos del vuelo en el formulario"""
        try:
            # Obtener datos del vuelo
            vuelo = self.cliente_api.obtener_vuelo(vuelo_id)
            
            # Llenar el formulario
            self.entry_numero.delete(0, "end")
            self.entry_numero.insert(0, vuelo.get('numero_vuelo', ''))
            
            self.entry_origen.delete(0, "end")
            self.entry_origen.insert(0, vuelo.get('origen', ''))
            
            self.entry_destino.delete(0, "end")
            self.entry_destino.insert(0, vuelo.get('destino', ''))
            
            # Fechas
            hora_salida = datetime.fromisoformat(vuelo.get('hora_salida'))
            self.entry_hora_salida.delete(0, "end")
            self.entry_hora_salida.insert(0, hora_salida.strftime("%Y-%m-%d %H:%M"))
            
            hora_llegada = datetime.fromisoformat(vuelo.get('hora_llegada'))
            self.entry_hora_llegada.delete(0, "end")
            self.entry_hora_llegada.insert(0, hora_llegada.strftime("%Y-%m-%d %H:%M"))
            
            # Estado
            self.combobox_estado.set(vuelo.get('estado', 'programado'))
            
            # Prioridad
            prioridad = vuelo.get('prioridad', 0)
            self.slider_prioridad.set(prioridad)
            self.label_valor_prioridad.configure(text=str(prioridad))
            
            # Emergencia
            if vuelo.get('emergencia', False):
                self.switch_emergencia.select()
            else:
                self.switch_emergencia.deselect()
                
        except Exception as e:
            self.manejar_error_api(e, "Error al cargar los datos del vuelo")
    
    def limpiar_formulario(self):
        """Limpia el formulario para crear un nuevo vuelo"""
        self.entry_numero.delete(0, "end")
        self.entry_origen.delete(0, "end")
        self.entry_destino.delete(0, "end")
        
        # Fechas por defecto (ahora y 2 horas después)
        ahora = datetime.now()
        self.entry_hora_salida.delete(0, "end")
        self.entry_hora_salida.insert(0, ahora.strftime("%Y-%m-%d %H:%M"))
        
        llegada = ahora + timedelta(hours=2)  # Fixed: using timedelta directly
        self.entry_hora_llegada.delete(0, "end")
        self.entry_hora_llegada.insert(0, llegada.strftime("%Y-%m-%d %H:%M"))
        
        # Valores por defecto
        self.combobox_estado.set("programado")
        self.slider_prioridad.set(50)
        self.label_valor_prioridad.configure(text="50")
        self.switch_emergencia.deselect()
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        # Validar campos obligatorios
        numero_vuelo = self.entry_numero.get()
        origen = self.entry_origen.get()
        destino = self.entry_destino.get()
        hora_salida = self.entry_hora_salida.get()
        hora_llegada = self.entry_hora_llegada.get()
        estado = self.combobox_estado.get()
        
        # Validar número de vuelo
        valido, mensaje = validar_texto_no_vacio(numero_vuelo)
        if not valido:
            return False, f"Número de vuelo: {mensaje}"
        
        # Validar origen
        valido, mensaje = validar_texto_no_vacio(origen)
        if not valido:
            return False, f"Origen: {mensaje}"
        
        # Validar destino
        valido, mensaje = validar_texto_no_vacio(destino)
        if not valido:
            return False, f"Destino: {mensaje}"
        
        # Validar hora de salida
        valido, mensaje = validar_fecha_hora(hora_salida)
        if not valido:
            return False, f"Hora de salida: {mensaje}"
        
        # Validar hora de llegada
        valido, mensaje = validar_fecha_hora(hora_llegada)
        if not valido:
            return False, f"Hora de llegada: {mensaje}"
        
        # Validar estado
        valido, mensaje = validar_estado_vuelo(estado)
        if not valido:
            return False, mensaje
        
        # Validar que la hora de llegada sea posterior a la de salida
        hora_salida_dt = convertir_a_fecha_hora(hora_salida)
        hora_llegada_dt = convertir_a_fecha_hora(hora_llegada)
        
        if hora_llegada_dt <= hora_salida_dt:
            return False, "La hora de llegada debe ser posterior a la hora de salida"
        
        return True, ""
    
    def obtener_datos_formulario(self):
        """Obtiene los datos del formulario como un diccionario"""
        datos = {
            "numero_vuelo": self.entry_numero.get(),
            "origen": self.entry_origen.get(),
            "destino": self.entry_destino.get(),
            "hora_salida": convertir_a_fecha_hora(self.entry_hora_salida.get()),
            "hora_llegada": convertir_a_fecha_hora(self.entry_hora_llegada.get()),
            "estado": self.combobox_estado.get(),
            "prioridad": int(self.slider_prioridad.get()),
            "emergencia": self.switch_emergencia.get()
        }
        
        # Incluir el ID si estamos en modo edición
        if self.modo_edicion and self.vuelo_id is not None:
            datos["id"] = self.vuelo_id
            
        return datos
    
    def guardar_vuelo(self):
        """Guarda o actualiza el vuelo según el modo"""
        # Validar formulario
        valido, mensaje = self.validar_formulario()
        if not valido:
            self.mostrar_error(mensaje)
            return
        
        # Obtener datos
        datos_vuelo = self.obtener_datos_formulario()
        
        try:
            if self.modo_edicion:
                # Asegurarnos de que el ID esté incluido en los datos
                if "id" not in datos_vuelo and self.vuelo_id is not None:
                    datos_vuelo["id"] = self.vuelo_id
                    
                # Actualizar vuelo existente
                self.cliente_api.actualizar_vuelo(self.vuelo_id, datos_vuelo)
                mensaje_exito = "Vuelo actualizado correctamente"
            else:
                # Crear nuevo vuelo
                self.cliente_api.crear_vuelo(datos_vuelo)
                mensaje_exito = "Vuelo creado correctamente"
            
            # Mostrar mensaje de éxito
            self.mostrar_mensaje("Éxito", mensaje_exito, "check")
            
            # Volver a la lista de vuelos
            self.controller.mostrar_vista("lista_vuelos")
            
        except Exception as e:
            self.manejar_error_api(e, "Error al guardar el vuelo")
    
    def cancelar(self):
        """Cancela la creación/edición y vuelve a la lista de vuelos"""
        self.controller.mostrar_vista("lista_vuelos")
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en el formulario"""
        self.logger.warning(f"Error en formulario: {mensaje}")
        self.label_error.configure(text=mensaje)
        self.frame_mensajes.grid(row=2, column=0, sticky="ew", pady=(0, 20))
