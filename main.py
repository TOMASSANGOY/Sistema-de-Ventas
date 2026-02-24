import tkinter as tk
from tkinter import ttk
import database
from ventas import Ventas
from productos import Productos
from historial import Historial
from contabilidad import Contabilidad
from clientes import Clientes

database.crear_tablas()  # crea todas las tablas incluidas clientes y fiados

root = tk.Tk()
root.title("Sistema de Ventas")
root.geometry("1000x700")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

ventas_tab = Ventas(notebook)
productos_tab = Productos(notebook)
historial_tab = Historial(notebook)
contabilidad_tab = Contabilidad(notebook)
clientes_tab = Clientes(notebook)

notebook.add(ventas_tab.frame, text="Ventas")
notebook.add(productos_tab.frame, text="Productos")
notebook.add(historial_tab.frame, text="Historial")
notebook.add(contabilidad_tab.frame, text="Contabilidad")
notebook.add(clientes_tab.frame, text="Clientes")

root.mainloop()