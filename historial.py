import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import database
from datetime import datetime


class Historial:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)

        tk.Label(
            self.frame,
            text="HISTORIAL DE VENTAS",
            font=("Arial", 16)
        ).pack(pady=10)

        fecha_frame = tk.Frame(self.frame)
        fecha_frame.pack(pady=5)

        tk.Label(fecha_frame, text="Seleccionar Fecha:").pack(side="left")

        self.fecha_entry = DateEntry(
            fecha_frame,
            date_pattern="yyyy-mm-dd",
            width=12
        )
        self.fecha_entry.pack(side="left", padx=5)

        tk.Button(
            fecha_frame,
            text="Buscar",
            command=self.buscar_por_fecha
        ).pack(side="left")

        # ===== LISTA DE VENTAS =====
        self.lista = tk.Listbox(self.frame, width=95, height=20)
        self.lista.pack(pady=10)
        self.lista.bind("<Double-Button-1>", self.ver_detalle)

        self.ventas_cache = []

        self.cargar_ventas()

    # ======================
    def buscar_por_fecha(self):
        fecha = self.fecha_entry.get()
        self.cargar_ventas(fecha)

    def cargar_ventas(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")

        self.lista.delete(0, tk.END)
        self.ventas_cache = database.obtener_historial_por_fecha(fecha)

        if not self.ventas_cache:
            self.lista.insert(tk.END, "No hay ventas.")
            return

        for v in self.ventas_cache:
            self.lista.insert(
                tk.END,
                f"ID {v[0]} | Total: ${v[1]} | Método: {v[2]} | Fecha: {v[3]}"
            )

    # ======================
    def ver_detalle(self, event=None):
        if not self.lista.curselection():
            return

        index = self.lista.curselection()[0]
        venta = self.ventas_cache[index]
        venta_id = venta[0]

        items = database.obtener_detalle_venta(venta_id)
        estado = database.obtener_estado_fiado(venta_id)
        # estado esperado:
        # None -> contado
        # (1, pagado, nombre_cliente) -> fiado

        ventana = tk.Toplevel(self.frame)
        ventana.title(f"Detalle Venta #{venta_id}")
        ventana.geometry("520x420")
        ventana.grab_set()

        texto = tk.Text(ventana, width=65, height=22)
        texto.pack(pady=10)

        texto.insert(tk.END, f"VENTA ID: {venta_id}\n")
        texto.insert(tk.END, "-" * 55 + "\n")

        total = 0
        for item in items:
            texto.insert(
                tk.END,
                f"{item[0]} | Cant: {item[1]} | Subtotal: ${item[2]}\n"
            )
            total += item[2]

        texto.insert(tk.END, "-" * 55 + "\n")
        texto.insert(tk.END, f"TOTAL: ${total}\n\n")

        # ===== FIADO / CONTADO =====
        if estado and estado[0] == 1:
            pagado = "PAGADO" if estado[1] == 1 else "PENDIENTE DE PAGO"
            cliente = estado[2] if estado[2] else "Sin nombre"

            texto.insert(
                tk.END,
                f"TIPO: FIADO (Cliente: {cliente})\n"
                f"ESTADO: {pagado}\n"
            )
        else:
            texto.insert(tk.END, "TIPO: CONTADO\n")

        texto.config(state="disabled")