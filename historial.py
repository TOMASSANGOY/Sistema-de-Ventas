import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import database
from datetime import datetime

class Historial:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        tk.Label(self.frame, text="HISTORIAL DE VENTAS", font=("Arial", 16)).pack(pady=10)

        fecha_frame = tk.Frame(self.frame)
        fecha_frame.pack(pady=5)

        tk.Label(fecha_frame, text="Seleccionar Fecha:").pack(side="left")

        self.fecha_entry = DateEntry(fecha_frame, date_pattern="yyyy-mm-dd", width=12)
        self.fecha_entry.pack(side="left", padx=5)

        tk.Button(fecha_frame, text="Buscar", command=self.buscar_por_fecha).pack(side="left")

        # Cambiamos Text por Listbox
        self.lista_ventas = tk.Listbox(self.frame, width=95, height=25)
        self.lista_ventas.pack(pady=10)

        # Bind doble clic
        self.lista_ventas.bind("<Double-Button-1>", self.mostrar_detalle_venta)

        # Cache para guardar datos de ventas mostradas
        self.ventas_cache = []

        # Carga inicial al abrir la pestaña
        self.cargar_ventas()

    # ====================== MÉTODOS ======================

    def buscar_por_fecha(self):
        fecha = self.fecha_entry.get()
        ventas = database.obtener_historial_por_fecha(fecha)

        self.lista_ventas.delete(0, tk.END)
        self.ventas_cache = ventas

        if not ventas:
            self.lista_ventas.insert(tk.END, "No hay ventas en esa fecha.")
            return

        for venta in ventas:
            self.lista_ventas.insert(
                tk.END,
                f"ID: {venta[0]} | Total: ${venta[1]} | Método: {venta[2]} | Fecha: {venta[3]}"
            )

    def cargar_ventas(self):
        """Carga todas las ventas del día actual en el Listbox"""
        fecha = datetime.now().strftime("%Y-%m-%d")
        ventas = database.obtener_historial_por_fecha(fecha)

        self.lista_ventas.delete(0, tk.END)
        self.ventas_cache = ventas

        if not ventas:
            self.lista_ventas.insert(tk.END, "No hay ventas hoy.")
            return

        for venta in ventas:
            self.lista_ventas.insert(
                tk.END,
                f"ID: {venta[0]} | Total: ${venta[1]} | Método: {venta[2]} | Fecha: {venta[3]}"
            )

    def mostrar_detalle_venta(self, event):
        """Al hacer doble clic, muestra los productos de la venta"""
        seleccion = self.lista_ventas.curselection()
        if not seleccion:
            return

        index = seleccion[0]
        if index >= len(self.ventas_cache):
            return

        venta_id = self.ventas_cache[index][0]
        detalles = database.obtener_detalle_venta(venta_id)

        if not detalles:
            messagebox.showinfo("Detalle Venta", "No hay productos registrados para esta venta.")
            return

        ventana_detalle = tk.Toplevel(self.frame)
        ventana_detalle.title(f"Detalle Venta ID: {venta_id}")

        tk.Label(ventana_detalle, text=f"Detalle de la Venta ID: {venta_id}", font=("Arial", 14)).pack(pady=10)

        listbox_detalle = tk.Listbox(ventana_detalle, width=60)
        listbox_detalle.pack(padx=10, pady=10)

        for producto in detalles:
            nombre, cantidad, subtotal = producto
            listbox_detalle.insert(tk.END, f"{nombre} | Cantidad: {cantidad} | Subtotal: ${subtotal}")

        tk.Button(ventana_detalle, text="Cerrar", command=ventana_detalle.destroy).pack(pady=5)