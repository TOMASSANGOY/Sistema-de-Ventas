import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "kiosco.db"

class CuentaCorriente:

    def __init__(self, master):
        self.frame = tk.Frame(master)

        tk.Label(self.frame, text="CUENTAS CORRIENTES", font=("Arial", 16)).pack(pady=10)

        # ============================
        # LISTA CLIENTES
        # ============================
        self.tabla_clientes = ttk.Treeview(self.frame, columns=("ID","Nombre","Deuda"), show="headings")
        self.tabla_clientes.heading("ID", text="ID")
        self.tabla_clientes.heading("Nombre", text="Nombre")
        self.tabla_clientes.heading("Deuda", text="Deuda Total")
        self.tabla_clientes.pack(fill="x", padx=10)

        tk.Button(self.frame, text="Ver Detalle", command=self.ver_detalle).pack(pady=5)

        self.cargar_clientes()

    # ============================
    # CARGAR CLIENTES CON DEUDA
    # ============================
    def cargar_clientes(self):
        for item in self.tabla_clientes.get_children():
            self.tabla_clientes.delete(item)

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre FROM clientes")
        clientes = cursor.fetchall()

        for cliente in clientes:
            cliente_id = cliente[0]

            # total fiado
            cursor.execute("""
                SELECT IFNULL(SUM(total),0)
                FROM ventas
                WHERE cliente_id = ? AND metodo_pago = 'FIADO'
            """, (cliente_id,))
            total_fiado = cursor.fetchone()[0]

            # total pagado
            cursor.execute("""
                SELECT IFNULL(SUM(monto),0)
                FROM pagos_cc
                WHERE cliente_id = ?
            """, (cliente_id,))
            total_pagado = cursor.fetchone()[0]

            deuda = total_fiado - total_pagado

            self.tabla_clientes.insert("", "end", values=(cliente_id, cliente[1], round(deuda,2)))

        conn.close()

    # ============================
    # DETALLE CLIENTE
    # ============================
    def ver_detalle(self):
        seleccionado = self.tabla_clientes.focus()
        if not seleccionado:
            messagebox.showwarning("Aviso", "Seleccioná un cliente")
            return

        datos = self.tabla_clientes.item(seleccionado)["values"]
        cliente_id = datos[0]
        nombre = datos[1]

        VentanaDetalle(self.frame, cliente_id, nombre, self)


class VentanaDetalle(tk.Toplevel):

    def __init__(self, master, cliente_id, nombre, parent):
        super().__init__(master)
        self.cliente_id = cliente_id
        self.parent = parent

        self.title(f"Cuenta Corriente - {nombre}")
        self.geometry("700x600")

        # ============================
        # VENTAS FIADAS
        # ============================
        tk.Label(self, text="VENTAS FIADAS", font=("Arial",12)).pack()

        self.tabla_fiado = ttk.Treeview(self, columns=("Fecha","Total"), show="headings")
        self.tabla_fiado.heading("Fecha", text="Fecha")
        self.tabla_fiado.heading("Total", text="Total")
        self.tabla_fiado.pack(fill="x", padx=10)

        # ============================
        # HISTORIAL PAGOS
        # ============================
        tk.Label(self, text="PAGOS REALIZADOS", font=("Arial",12)).pack(pady=10)

        self.tabla_pagos = ttk.Treeview(self, columns=("Fecha","Monto"), show="headings")
        self.tabla_pagos.heading("Fecha", text="Fecha")
        self.tabla_pagos.heading("Monto", text="Monto")
        self.tabla_pagos.pack(fill="x", padx=10)

        # ============================
        # REGISTRAR PAGO
        # ============================
        tk.Label(self, text="Registrar Pago").pack(pady=5)
        self.entry_monto = tk.Entry(self)
        self.entry_monto.pack()

        tk.Button(self, text="Guardar Pago", command=self.registrar_pago).pack(pady=5)

        self.cargar_datos()

    # ============================
    # CARGAR DATOS
    # ============================
    def cargar_datos(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        for item in self.tabla_fiado.get_children():
            self.tabla_fiado.delete(item)

        cursor.execute("""
            SELECT fecha, total
            FROM ventas
            WHERE cliente_id = ? AND metodo_pago = 'FIADO'
        """, (self.cliente_id,))
        for row in cursor.fetchall():
            self.tabla_fiado.insert("", "end", values=row)

        for item in self.tabla_pagos.get_children():
            self.tabla_pagos.delete(item)

        cursor.execute("""
            SELECT fecha, monto
            FROM pagos_cc
            WHERE cliente_id = ?
        """, (self.cliente_id,))
        for row in cursor.fetchall():
            self.tabla_pagos.insert("", "end", values=row)

        conn.close()

    # ============================
    # REGISTRAR PAGO
    # ============================
    def registrar_pago(self):
        try:
            monto = float(self.entry_monto.get())
        except:
            messagebox.showerror("Error", "Monto inválido")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Guardar pago en cuenta corriente
        cursor.execute("""
            INSERT INTO pagos_cc (cliente_id, monto, fecha)
            VALUES (?, ?, ?)
        """, (self.cliente_id, monto, fecha))

        # Registrar ingreso en caja
        cursor.execute("""
            INSERT INTO ventas (fecha, total, metodo_pago, cliente_id)
            VALUES (?, ?, ?, ?)
        """, (fecha, monto, "PAGO_CC", self.cliente_id))

        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Pago registrado correctamente")

        self.entry_monto.delete(0, tk.END)
        self.cargar_datos()
        self.parent.cargar_clientes()