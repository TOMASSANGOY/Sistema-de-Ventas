import tkinter as tk
from tkinter import ttk
import database
import theme

# Crear la ventana ANTES de importar cualquier módulo que use matplotlib
root = tk.Tk()
root.title("Sistema de Ventas · Kiosco")
root.geometry("1100x720")
root.configure(bg=theme.BG_ROOT)
root.minsize(900, 600)

database.crear_tablas()
theme.apply_ttk_style()

# Importar módulos DESPUÉS de crear root (evita ventana tk fantasma de matplotlib)
from ventas import Ventas
from productos import Productos
from historial import Historial
from contabilidad import Contabilidad
from clientes import Clientes
from egresos import Egresos

# Header
header = tk.Frame(root, bg=theme.BG_CARD, height=52)
header.pack(fill="x")
header.pack_propagate(False)
tk.Label(
    header, text="🏪  KIOSCO — Sistema de Ventas",
    font=theme.FONT_HEADING,
    bg=theme.BG_CARD, fg=theme.ACCENT
).pack(side="left", padx=20, pady=12)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tabs = [
    (Ventas,       "🛒  Ventas"),
    (Productos,    "📦  Productos"),
    (Historial,    "📋  Historial"),
    (Contabilidad, "📊  Contabilidad"),
    (Clientes,     "👥  Clientes"),
    (Egresos,      "💸  Egresos"),
]

for cls, nombre in tabs:
    tab = cls(notebook)
    notebook.add(tab.frame, text=nombre)

root.mainloop()
