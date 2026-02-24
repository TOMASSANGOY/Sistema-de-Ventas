import tkinter as tk
from tkinter import messagebox
import database

class Clientes:

    def __init__(self, parent):

        self.frame = tk.Frame(parent)
        self.frame.pack(padx=10, pady=10, fill="both", expand=True)

        tk.Label(self.frame, text="CLIENTES", font=("Arial", 16)).pack(pady=10)

        # ===== CAMPOS =====
        tk.Label(self.frame, text="Nombre").pack()
        self.entry_nombre = tk.Entry(self.frame)
        self.entry_nombre.pack()

        tk.Label(self.frame, text="Teléfono").pack()
        self.entry_telefono = tk.Entry(self.frame)
        self.entry_telefono.pack()

        tk.Label(self.frame, text="Dirección").pack()
        self.entry_direccion = tk.Entry(self.frame)
        self.entry_direccion.pack()

        tk.Label(self.frame, text="Email").pack()
        self.entry_email = tk.Entry(self.frame)
        self.entry_email.pack()

        # ===== BOTONES =====
        self.btn_agregar = tk.Button(self.frame, text="Agregar Cliente", command=self.agregar)
        self.btn_agregar.pack(pady=5)

        self.btn_editar = tk.Button(self.frame, text="Editar Cliente", bg="blue", fg="white", command=self.cargar_para_editar)
        self.btn_editar.pack(pady=5)

        self.btn_guardar = tk.Button(self.frame, text="Guardar Cambios", bg="green", fg="white", command=self.guardar_cambios, state="disabled")
        self.btn_guardar.pack(pady=5)

        self.btn_cancelar = tk.Button(self.frame, text="Cancelar Edición", bg="orange", command=self.cancelar_edicion, state="disabled")
        self.btn_cancelar.pack(pady=5)

        self.btn_eliminar = tk.Button(self.frame, text="Eliminar Cliente Seleccionado", bg="red", fg="white", command=self.eliminar)
        self.btn_eliminar.pack(pady=5)

        # ===== LISTA =====
        self.lista = tk.Listbox(self.frame, width=90)
        self.lista.pack(pady=10)

        self.clientes_cache = []
        self.cliente_editando_id = None

        self.cargar_clientes()

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
        self.cliente_editando_id = None

    # ================= AGREGAR =================
    def agregar(self):

        nombre, telefono, direccion, email = self.obtener_datos()
        if nombre is None:
            return

        database.agregar_cliente(nombre, telefono, direccion, email)
        self.limpiar_campos()
        self.cargar_clientes()

    # ================= EDITAR =================
    def cargar_para_editar(self):

        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná un cliente")
            return

        index = seleccion[0]
        cliente = self.clientes_cache[index]

        self.cliente_editando_id = cliente[0]

        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, cliente[1])

        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, cliente[2] or "")

        self.entry_direccion.delete(0, tk.END)
        self.entry_direccion.insert(0, cliente[3] or "")

        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, cliente[4] or "")

        self.activar_modo_edicion()

    def guardar_cambios(self):

        if self.cliente_editando_id is None:
            return

        nombre, telefono, direccion, email = self.obtener_datos()
        if nombre is None:
            return

        database.editar_cliente(self.cliente_editando_id, nombre, telefono, direccion, email)

        self.limpiar_campos()
        self.cargar_clientes()
        self.desactivar_modo_edicion()

        messagebox.showinfo("Éxito", "Cliente actualizado correctamente")

    # ================= CANCELAR =================
    def cancelar_edicion(self):
        self.limpiar_campos()
        self.desactivar_modo_edicion()

    # ================= ELIMINAR =================
    def eliminar(self):

        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccioná un cliente")
            return

        confirmar = messagebox.askyesno("Confirmar", "¿Seguro que querés eliminar este cliente?")
        if not confirmar:
            return

        index = seleccion[0]
        cliente_id = self.clientes_cache[index][0]

        database.eliminar_cliente(cliente_id)
        self.cargar_clientes()
        self.limpiar_campos()
        self.desactivar_modo_edicion()

    # ================= UTILIDADES =================
    def obtener_datos(self):

        nombre = self.entry_nombre.get().strip()
        telefono = self.entry_telefono.get().strip()
        direccion = self.entry_direccion.get().strip()
        email = self.entry_email.get().strip()

        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return None, None, None, None

        return nombre, telefono, direccion, email

    def limpiar_campos(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_direccion.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)

    def cargar_clientes(self):

        self.lista.delete(0, tk.END)
        self.clientes_cache = database.obtener_clientes()

        for c in self.clientes_cache:
            self.lista.insert(tk.END, f"{c[1]} | Tel: {c[2] or ''} | Dir: {c[3] or ''} | Email: {c[4] or ''}")