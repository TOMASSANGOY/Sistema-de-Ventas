import tkinter as tk
from tkinter import messagebox, simpledialog
import database

class Ventas:

    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.carrito = []
        self.total = 0

        tk.Label(self.frame, text="VENTAS", font=("Arial", 18)).pack(pady=10)

        # ===== BUSCADOR DE PRODUCTOS =====
        tk.Label(self.frame, text="Buscar producto").pack()
        self.buscador = tk.Entry(self.frame, width=40)
        self.buscador.pack()
        self.buscador.focus()
        self.buscador.bind("<KeyRelease>", self.buscar_producto)
        self.buscador.bind("<Down>", self.bajar_a_lista)

        self.lista_productos = tk.Listbox(self.frame, width=80, height=6)
        self.lista_productos.pack(pady=5)
        self.lista_productos.bind("<Return>", self.seleccionar_producto)
        self.lista_productos.bind("<Double-Button-1>", self.seleccionar_producto)

        # ===== CARRITO =====
        tk.Label(self.frame, text="Carrito").pack()
        self.lista_carrito = tk.Listbox(self.frame, width=80, height=8)
        self.lista_carrito.pack()

        tk.Button(self.frame, text="Eliminar del carrito",
                  bg="red", fg="white",
                  command=self.eliminar_del_carrito).pack(pady=5)

        self.label_total = tk.Label(self.frame, text="Total: $0", font=("Arial", 14))
        self.label_total.pack(pady=10)

        # ===== BOTONES DE PAGO =====
        tk.Button(self.frame, text="Cobrar",
                  bg="green", fg="white",
                  command=self.abrir_ventana_pago).pack(pady=5)

    # ================= FUNCIONES =================
    def buscar_producto(self, event=None):
        texto = self.buscador.get()
        productos = database.buscar_productos(texto)
        self.lista_productos.delete(0, tk.END)
        for p in productos:
            self.lista_productos.insert(
                tk.END,
                f"{p[0]} | {p[1]} | ${p[2]} | Stock: {p[3]}"
            )

    def bajar_a_lista(self, event):
        if self.lista_productos.size() > 0:
            self.lista_productos.focus()
            self.lista_productos.selection_set(0)

    def seleccionar_producto(self, event=None):
        if not self.lista_productos.curselection():
            return
        index = self.lista_productos.curselection()[0]
        producto = self.lista_productos.get(index)
        datos = producto.split(" | ")
        producto_id = int(datos[0])
        nombre = datos[1]
        precio = float(datos[2].replace("$", ""))
        stock = int(datos[3].replace("Stock: ", ""))
        self.pedir_cantidad(producto_id, nombre, precio, stock)

    def pedir_cantidad(self, producto_id, nombre, precio, stock):
        ventana = tk.Toplevel(self.frame)
        ventana.title("Cantidad")
        ventana.geometry("250x150")
        ventana.grab_set()
        tk.Label(ventana, text=f"{nombre}\nStock: {stock}").pack(pady=5)
        cantidad_entry = tk.Entry(ventana)
        cantidad_entry.pack()
        cantidad_entry.focus()

        def confirmar(event=None):
            try:
                cantidad = int(cantidad_entry.get())
                if cantidad <= 0 or cantidad > stock:
                    raise ValueError
                subtotal = precio * cantidad
                self.carrito.append((producto_id, nombre, precio, cantidad, subtotal))
                self.actualizar_carrito()
                ventana.destroy()
                self.buscador.focus()
            except:
                messagebox.showerror("Error", "Cantidad inválida")

        cantidad_entry.bind("<Return>", confirmar)
        tk.Button(ventana, text="Agregar", command=confirmar).pack(pady=5)

    def actualizar_carrito(self):
        self.lista_carrito.delete(0, tk.END)
        self.total = 0
        for item in self.carrito:
            self.lista_carrito.insert(
                tk.END,
                f"{item[1]} x{item[3]} - ${item[4]}"
            )
            self.total += item[4]
        self.label_total.config(text=f"Total: ${self.total}")

    def eliminar_del_carrito(self):
        if not self.lista_carrito.curselection():
            return
        index = self.lista_carrito.curselection()[0]
        self.carrito.pop(index)
        self.actualizar_carrito()

    # ================= PAGO =================
    def abrir_ventana_pago(self):
        if not self.carrito:
            messagebox.showwarning("Atención", "Carrito vacío")
            return

        ventana_pago = tk.Toplevel(self.frame)
        ventana_pago.title("Método de Pago")
        ventana_pago.geometry("300x250")
        ventana_pago.grab_set()

        tk.Label(ventana_pago, text="Seleccionar método de pago", font=("Arial", 12)).pack(pady=10)

        tk.Button(ventana_pago, text="Efectivo", width=20,
                  command=lambda: self.confirmar_pago("Efectivo", ventana_pago)).pack(pady=5)
        tk.Button(ventana_pago, text="Débito", width=20,
                  command=lambda: self.confirmar_pago("Débito", ventana_pago)).pack(pady=5)
        tk.Button(ventana_pago, text="Transferencia", width=20,
                  command=lambda: self.confirmar_pago("Transferencia", ventana_pago)).pack(pady=5)
        tk.Button(ventana_pago, text="Fiado (Cuenta Corriente)", width=25,
                  command=lambda: self.seleccionar_cliente_fiado(ventana_pago)).pack(pady=5)

    def confirmar_pago(self, metodo, ventana_pago):
        database.registrar_venta(self.carrito, metodo)
        messagebox.showinfo("Éxito", "Venta registrada correctamente")
        self.carrito.clear()
        self.actualizar_carrito()
        self.buscador.delete(0, tk.END)
        self.buscador.focus()
        ventana_pago.destroy()

    # ================= FIADOS =================
    def seleccionar_cliente_fiado(self, ventana_pago):
        clientes = database.obtener_clientes()
        if not clientes:
            messagebox.showerror("Error", "No hay clientes registrados")
            return

        # ventana simple con Listbox para seleccionar cliente
        win = tk.Toplevel(self.frame)
        win.title("Seleccionar Cliente para Fiado")
        win.geometry("300x300")
        win.grab_set()

        tk.Label(win, text="Seleccionar cliente:").pack(pady=5)
        listbox = tk.Listbox(win, width=40, height=10)
        listbox.pack(pady=5)

        for c in clientes:
            listbox.insert(tk.END, f"{c[0]} | {c[1]}")

        def confirmar():
            if not listbox.curselection():
                messagebox.showerror("Error", "Seleccioná un cliente")
                return
            index = listbox.curselection()[0]
            cliente_id = clientes[index][0]
            cliente_nombre = clientes[index][1]
            database.registrar_venta(self.carrito, fiado=True, cliente_id=cliente_id)
            messagebox.showinfo("Éxito", f"Venta registrada a fiado para {cliente_nombre}")
            self.carrito.clear()
            self.actualizar_carrito()
            self.buscador.delete(0, tk.END)
            self.buscador.focus()
            win.destroy()
            ventana_pago.destroy()

        tk.Button(win, text="Confirmar", command=confirmar).pack(pady=5)