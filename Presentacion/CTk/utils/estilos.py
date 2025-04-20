"""
Definiciones de estilos y temas para la aplicación.
"""
import customtkinter as ctk

# Configuración global de CustomTkinter
ctk.set_appearance_mode("System")  # "System", "Dark" o "Light"
ctk.set_default_color_theme("blue")  # "blue", "dark-blue" o "green"

# Paleta de colores personalizados
COLORES = {
    "primary": "#0078D7",
    "secondary": "#5B9BD5",
    "accent": "#FF8C00",
    "success": "#28A745",
    "warning": "#FFC107",
    "danger": "#DC3545",
    "info": "#17A2B8",
    "light": "#F8F9FA",
    "dark": "#343A40",
    "emergency": "#FF0000"
}

# Estilos para widgets
ESTILOS = {
    "frame": {
        "fg_color": None,  # Color transparente
        "border_width": 0,
        "corner_radius": 10
    },
    "card_frame": {
        "fg_color": ("gray90", "gray20"),
        "border_width": 1,
        "corner_radius": 10
    },
    "button": {
        "fg_color": COLORES["primary"],
        "hover_color": COLORES["secondary"],
        "border_width": 0,
        "corner_radius": 8,
        "text_color": "white",
        "cursor": "hand2"  # Add cursor style for buttons
    },
    "danger_button": {
        "fg_color": COLORES["danger"],
        "hover_color": "#c82333",
        "border_width": 0,
        "corner_radius": 8,
        "text_color": "white",
        "cursor": "hand2"  # Add cursor style for danger buttons
    },
    "success_button": {
        "fg_color": COLORES["success"],
        "hover_color": "#218838",
        "border_width": 0,
        "corner_radius": 8,
        "text_color": "white",
        "cursor": "hand2"  # Add cursor style for success buttons
    },
    "label": {
        "text_color": None,  # Color por defecto del tema
        "corner_radius": 0
    },
    "entry": {
        "fg_color": ("gray95", "gray25"),
        "border_width": 1,
        "corner_radius": 8
    },
    "emergency_frame": {
        "fg_color": "#ffebee",  # Fondo rojo claro
        "border_width": 1,
        "border_color": COLORES["danger"],
        "corner_radius": 8
    }
}

def aplicar_estilo(widget, estilo: str) -> None:
    """Aplica un estilo predefinido a un widget"""
    if estilo in ESTILOS:
        for prop, value in ESTILOS[estilo].items():
            if hasattr(widget, f"configure_{prop}"):
                method = getattr(widget, f"configure_{prop}")
                method(value)
            elif hasattr(widget, "configure"):
                widget.configure(**{prop: value})
                
            # Special handling for cursor
            if prop == "cursor" and hasattr(widget, "_canvas"):
                widget._canvas.config(cursor=value)
                
        # For buttons, make sure all child widgets are clickable
        if estilo in ["button", "danger_button", "success_button"] and hasattr(widget, "_canvas"):
            # Make the entire button area clickable by binding event to all components
            if hasattr(widget, "_text_label") and widget._text_label:
                widget._text_label.configure(cursor="hand2")
                
            # Make sure clicks on any part of the button work
            def ensure_button_command(event):
                if hasattr(widget, "_command") and widget._command:
                    widget._command()
            
            # Bind to internal widgets if text label exists
            if hasattr(widget, "_text_label") and widget._text_label:
                widget._text_label.bind("<Button-1>", ensure_button_command)
                
            # Solve the dead zone issue directly
            if hasattr(widget, "_canvas"):
                widget._canvas.bind("<Button-1>", ensure_button_command)
