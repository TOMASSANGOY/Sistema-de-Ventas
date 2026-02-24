import tkinter as tk
from tkinter import messagebox
import models

class Productos:

    def __init__(self, parent):

        self.frame = tk.Frame(parent)

        tk.Label(self.frame, text="PRODUCTOS", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.frame, text="Nombre").pack()
        self.entry_nombre = tk.Entry(self.frame)
        self.entry_nombre.pack()

        tk.Label(self.frame, text="Precio Costo").pack()
        self.entry_costo = tk.Entry(self.frame)
        self.entry_costo.pack()

        tk.Label(self.frame, text="Precio Venta").pack()
        self.entry_venta = tk.Entry(self.frame)
        self.entry_venta.pack()

        tk.Label(self.frame, text="Stock").pack()
        self.entry_stock = tk.Entry(self.frame)
        self.entry_stock.pack()

        # ===== BOTONES =====

        self.btn_agregar = tk.Button(
            self.frame,
            text="Agregar Producto",
            command=self.agregar
        )
        self.btn_agregar.pack(pady=5)

        self.btn_editar = tk.Button(
            self.frame,
            text="Editar Producto",
            bg="blue",
            fg="white",
            command=self.cargar_para_editar
        )
        self.btn_editar.pack(pady=5)

        self.btn_guardar = tk.Button(
            self.frame,
            text="Guardar Cambios",
            bg="green",
            fg="white",
            command=self.guardar_cambios,
            state="disabled"
        )
        self.btn_guardar.pack(pady=5)

        self.btn_cancelar = tk.Button(
            self.frame,
            text="Cancelar Edición",
            bg="orange",
            command=self.cancelar_edicion,
            state="disabled"
        )
        self.btn_cancelar.pack(pady=5)

        self.btn_eliminar = tk.Button(
            self.frame,
            text="Eliminar Producto Seleccionado",
            bg="red",
            fg="white",
            command=self.eliminar
        )
        self.btn_eliminar.pack(pady=5)

        self.lista = tk.Listbox(self.frame, width=90)
        self.lista.pack(pady=10)

        self.productos_cache = []
        self.producto_editando_id = None

        self.cargar_productos()

    # ================= MODO EDICIÓN =================

    def activar_modo_edicion(self):
        self.btn_agregar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.btn_guardar.config(state="normal")
        self.btn_cancelar.config(state="normal")

    def desactivar_modo_edicion(self):
        self.btn_agregar.config(state="normal")
        self.btn_eliminar.config(state="normal")
        self.btn_guardar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")
        self.producto_editando_id = None

    # ================= AGREGAR =================

    def agregar(self):

        nombre, costo, venta, stock = self.obtener_datos()

        if nombre is None:
            return

        models.agregar_producto(nombre, costo, venta, stock)
        self.limpiar_campos()
        self.cargar_productos()

    # ================= EDITAR =================

    def cargar_para_editar(self):

        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná un producto")
            return

        index = seleccion[0]
        producto = self.productos_cache[index]

        self.producto_editando_id = producto[0]

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, producto[1])

        self.entry_costo.delete(0, tk.END)
        self.entry_costo.insert(0, producto[2])

        self.entry_venta.delete(0, tk.END)
        self.entry_venta.insert(0, producto[3])

        self.entry_stock.delete(0, tk.END)
        self.entry_stock.insert(0, producto[4])

        self.activar_modo_edicion()

    def guardar_cambios(self):

        if self.producto_editando_id is None:
            return

        nombre, costo, venta, stock = self.obtener_datos()

        if nombre is None:
            return

        models.editar_producto(
            self.producto_editando_id,
            nombre,
            costo,
            venta,
            stock
        )

        self.limpiar_campos()
        self.cargar_productos()
        self.desactivar_modo_edicion()

        messagebox.showinfo("Éxito", "Producto actualizado correctamente")

    # ================= CANCELAR =================

    def cancelar_edicion(self):
        self.limpiar_campos()
        self.desactivar_modo_edicion()

    # ================= ELIMINAR =================

    def eliminar(self):

        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná un producto")
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            "¿Seguro que querés eliminar este producto?"
        )

        if not confirmar:
            return

        index = seleccion[0]
        producto_id = self.productos_cache[index][0]

        models.eliminar_producto(producto_id)
        self.cargar_productos()

    # ================= UTILIDADES =================

    def obtener_datos(self):

        nombre = self.entry_nombre.get().strip()
        costo = self.entry_costo.get()
        venta = self.entry_venta.get()
        stock = self.entry_stock.get()

        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return None, None, None, None

        try:
            costo = float(costo)
            venta = float(venta)
            stock = int(stock)
        except:
            messagebox.showerror("Error", "Datos inválidos")
            return None, None, None, None

        if costo < 0 or venta < 0 or stock < 0:
            messagebox.showerror("Error", "No se permiten valores negativos")
            return None, None, None, None

        return nombre, costo, venta, stock

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_costo.delete(0, tk.END)
        self.entry_venta.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)

    def cargar_productos(self):

        self.lista.delete(0, tk.END)
        self.productos_cache = models.obtener_todos_productos()

        for p in self.productos_cache:
            ganancia = p[3] - p[2]
            self.lista.insert(
                tk.END,
                f"{p[1]} | Costo: ${p[2]} | Venta: ${p[3]} | Ganancia: ${ganancia} | Stock: {p[4]}"
            )