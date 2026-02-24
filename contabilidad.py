import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt

DB_NAME = "kiosco.db"

class Contabilidad:

    def __init__(self, master):

        self.frame = tk.Frame(master)

        # ===============================
        # CAJA POR FECHA
        # ===============================
        frame_fecha = tk.LabelFrame(self.frame, text="Caja por Fecha")
        frame_fecha.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_fecha, text="Fecha:").pack(side="left", padx=5)

        self.calendario = DateEntry(
            frame_fecha,
            width=12,
            background='darkblue',
            foreground='white',
            date_pattern='yyyy-mm-dd'
        )
        self.calendario.pack(side="left", padx=5)

        tk.Button(frame_fecha, text="Ver Caja", command=self.ver_caja_fecha).pack(side="left", padx=5)
        tk.Button(frame_fecha, text="Ganancia Neta Día", command=self.ver_ganancia_neta_dia).pack(side="left", padx=5)
        tk.Button(frame_fecha, text="Gráfico Métodos", command=self.grafico_metodos).pack(side="left", padx=5)

        # ===============================
        # GANANCIA POR MES
        # ===============================
        frame_mes = tk.LabelFrame(self.frame, text="Ganancia por Mes")
        frame_mes.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_mes, text="Mes:").pack(side="left", padx=5)

        self.combo_mes = ttk.Combobox(frame_mes, state="readonly")
        self.combo_mes.pack(side="left", padx=5)

        tk.Button(frame_mes, text="Ver Mes", command=self.ver_ganancia_mes).pack(side="left", padx=5)
        tk.Button(frame_mes, text="Ganancia Neta Mes", command=self.ver_ganancia_neta_mes).pack(side="left", padx=5)

        # ===============================
        # RESULTADOS
        # ===============================
        self.texto = tk.Text(self.frame, height=15)
        self.texto.pack(fill="both", expand=True, padx=10, pady=10)

        self.cargar_meses_disponibles()

    # ===============================
    # CARGAR MESES
    # ===============================
    def cargar_meses_disponibles(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT substr(fecha, 1, 7)
            FROM ventas
            ORDER BY fecha DESC
        """)
        meses = [fila[0] for fila in cursor.fetchall()]
        conn.close()

        self.combo_mes["values"] = meses
        if meses:
            self.combo_mes.current(0)

    # ===============================
    # CAJA POR FECHA
    # ===============================
    def ver_caja_fecha(self):
        fecha = self.calendario.get()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*), SUM(total)
            FROM ventas
            WHERE substr(fecha,1,10) = ?
        """, (fecha,))
        ventas, total = cursor.fetchone()

        cursor.execute("""
            SELECT metodo_pago, SUM(total)
            FROM ventas
            WHERE substr(fecha,1,10) = ?
            GROUP BY metodo_pago
        """, (fecha,))
        metodos = cursor.fetchall()
        conn.close()

        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, f"===== CAJA DEL {fecha} =====\n\n")
        self.texto.insert(tk.END, f"Ventas: {ventas or 0}\n")
        self.texto.insert(tk.END, f"Total vendido: ${total or 0}\n\n")
        self.texto.insert(tk.END, "Por método:\n")
        for metodo, monto in metodos:
            self.texto.insert(tk.END, f"{metodo}: ${monto}\n")

    # ===============================
    # GANANCIA NETA DÍA (RESUMEN COMPLETO)
    # ===============================
    def ver_ganancia_neta_dia(self):
        fecha = self.calendario.get()
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Total vendido y costo total
        cursor.execute("""
            SELECT IFNULL(SUM(d.subtotal),0), IFNULL(SUM(p.precio_costo * d.cantidad),0)
            FROM detalle_venta d
            JOIN productos p ON d.producto_id = p.id
            JOIN ventas v ON d.venta_id = v.id
            WHERE substr(v.fecha,1,10) = ?
        """, (fecha,))
        total_vendido, costo_total = cursor.fetchone()
        ganancia = total_vendido - costo_total
        conn.close()

        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, f"===== RESUMEN DEL {fecha} =====\n\n")
        self.texto.insert(tk.END, f"Total vendido: ${round(total_vendido,2)}\n")
        self.texto.insert(tk.END, f"Costo total: ${round(costo_total,2)}\n")
        self.texto.insert(tk.END, f"Ganancia neta: ${round(ganancia,2)}\n")

    # ===============================
    # GRAFICO
    # ===============================
    def grafico_metodos(self):
        fecha = self.calendario.get()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT metodo_pago, SUM(total)
            FROM ventas
            WHERE substr(fecha,1,10) = ?
            GROUP BY metodo_pago
        """, (fecha,))
        datos = cursor.fetchall()
        conn.close()

        if not datos:
            messagebox.showinfo("Info", "No hay datos para esa fecha.")
            return

        metodos = [d[0] for d in datos]
        montos = [d[1] for d in datos]

        plt.figure()
        plt.bar(metodos, montos)
        plt.title(f"Métodos de Pago - {fecha}")
        plt.xlabel("Método")
        plt.ylabel("Monto")
        plt.show()

    # ===============================
    # GANANCIA POR MES
    # ===============================
    def ver_ganancia_mes(self):
        mes = self.combo_mes.get()
        if not mes:
            messagebox.showwarning("Aviso", "No hay meses disponibles.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*), SUM(total)
            FROM ventas
            WHERE substr(fecha,1,7) = ?
        """, (mes,))
        ventas, total = cursor.fetchone()
        conn.close()

        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, f"===== GANANCIA DEL {mes} =====\n\n")
        self.texto.insert(tk.END, f"Ventas totales: {ventas or 0}\n")
        self.texto.insert(tk.END, f"Ingreso total: ${total or 0}\n")

    # ===============================
    # GANANCIA NETA MES (RESUMEN COMPLETO)
    # ===============================
    def ver_ganancia_neta_mes(self):
        mes = self.combo_mes.get()
        if not mes:
            messagebox.showwarning("Aviso", "No hay meses disponibles.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT IFNULL(SUM(d.subtotal),0), IFNULL(SUM(p.precio_costo * d.cantidad),0)
            FROM detalle_venta d
            JOIN productos p ON d.producto_id = p.id
            JOIN ventas v ON d.venta_id = v.id
            WHERE substr(v.fecha,1,7) = ?
        """, (mes,))
        total_vendido, costo_total = cursor.fetchone()
        ganancia = total_vendido - costo_total
        conn.close()

        self.texto.delete("1.0", tk.END)
        self.texto.insert(tk.END, f"===== RESUMEN DEL {mes} =====\n\n")
        self.texto.insert(tk.END, f"Total vendido: ${round(total_vendido,2)}\n")
        self.texto.insert(tk.END, f"Costo total: ${round(costo_total,2)}\n")
        self.texto.insert(tk.END, f"Ganancia neta: ${round(ganancia,2)}\n")