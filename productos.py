import tkinter as tk
from tkinter import messagebox
import database
import theme


class Productos:

    def __init__(self, parent):
        self.frame = theme.frame(parent)
        self.productos_cache = []
        self.producto_editando_id = None

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # Título
        title_bar = theme.frame(self.frame, bg=theme.BG_CARD)
        title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        theme.label(title_bar, "📦  Gestión de Productos", style="title", bg=theme.BG_CARD).pack(side="left", padx=20, pady=14)

        # ── Formulario ───────────────────────────────
        form = theme.card(self.frame, title=" Nuevo / Editar producto")
        form.grid(row=1, column=0, sticky="ns", padx=12, pady=10)

        campos = [
            ("Nombre",        "entry_nombre"),
            ("Precio Costo",  "entry_costo"),
            ("Precio Venta",  "entry_venta"),
            ("Stock",         "entry_stock"),
        ]
        for label_txt, attr in campos:
            theme.label(form, label_txt, bg=theme.BG_CARD).pack(anchor="w", padx=12, pady=(8,0))
            e = theme.entry(form, width=24)
            e.pack(padx=12, pady=2)
            setattr(self, attr, e)

        theme.separator(form).pack(fill="x", padx=12, pady=10)

        self.btn_agregar = theme.btn_success(form, "＋  Agregar", self.agregar, width=20)
        self.btn_agregar.pack(pady=3)
        self.btn_editar = theme.btn_info(form, "✎  Editar seleccionado", self.cargar_para_editar, width=20)
        self.btn_editar.pack(pady=3)
        self.btn_guardar = theme.btn_success(form, "✔  Guardar cambios", self.guardar_cambios, width=20, state="disabled")
        self.btn_guardar.pack(pady=3)
        self.btn_cancelar = theme.btn_warning(form, "✕  Cancelar", self.cancelar_edicion, width=20, state="disabled")
        self.btn_cancelar.pack(pady=3)
        self.btn_eliminar = theme.btn_danger(form, "🗑  Eliminar", self.eliminar, width=20)
        self.btn_eliminar.pack(pady=3)
        theme.separator(form).pack(fill="x", padx=12, pady=6)
        theme.btn_ghost(form, "📈  Ver historial de precios", self.ver_historial_precios, width=20).pack(pady=3)

        # ── Lista ────────────────────────────────────
        list_panel = theme.card(self.frame, title=" Productos en stock")
        list_panel.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)
        list_panel.rowconfigure(0, weight=1)
        list_panel.columnconfigure(0, weight=1)

        lf, self.lista = theme.scrolled_listbox(list_panel, width=70, height=22)
        lf.pack(fill="both", expand=True, padx=8, pady=8)

        self.cargar_productos()

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

    def agregar(self):
        datos = self.obtener_datos()
        if datos[0] is None:
            return
        database.agregar_producto(*datos)
        self.limpiar_campos()
        self.cargar_productos()

    def cargar_para_editar(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showerror("Error", "Seleccioná un producto de la lista")
            return
        p = self.productos_cache[sel[0]]
        self.producto_editando_id = p[0]
        for entry, val in zip(
            [self.entry_nombre, self.entry_costo, self.entry_venta, self.entry_stock],
            p[1:]
        ):
            entry.delete(0, tk.END)
            entry.insert(0, val)
        self.activar_modo_edicion()

    def guardar_cambios(self):
        if self.producto_editando_id is None:
            return
        datos = self.obtener_datos()
        if datos[0] is None:
            return
        database.editar_producto(self.producto_editando_id, *datos)
        self.limpiar_campos()
        self.cargar_productos()
        self.desactivar_modo_edicion()
        self._toast("✓  Producto actualizado")

    def _toast(self, texto, color=None):
        lbl = tk.Label(
            self.frame, text=texto,
            font=theme.FONT_BODY,
            bg=color or theme.SUCCESS, fg="white",
            padx=16, pady=8
        )
        lbl.place(relx=0.5, rely=0.97, anchor="s")
        lbl.after(2000, lbl.destroy)

    def ver_historial_precios(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showerror("Error", "Seleccioná un producto de la lista.")
            return
        p = self.productos_cache[sel[0]]
        historial = database.obtener_historial_precios(p[0])

        win = tk.Toplevel(self.frame)
        win.title(f"Historial de precios — {p[1]}")
        win.geometry("460x360")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()

        theme.label(win, f"📈  {p[1]}", style="heading", bg=theme.BG_PANEL).pack(pady=12)
        theme.label(win, f"Precio actual:  Costo ${p[2]:.2f}  /  Venta ${p[3]:.2f}",
                    bg=theme.BG_PANEL, fg=theme.ACCENT2).pack()

        theme.separator(win).pack(fill="x", padx=16, pady=8)

        if not historial:
            theme.label(win, "Sin cambios de precio registrados aún.",
                        bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(pady=20)
        else:
            lf, lb = theme.scrolled_listbox(win, width=56, height=12)
            lf.pack(padx=14, pady=4, fill="both", expand=True)
            lb.insert(tk.END, f"  {'FECHA':<22}  {'COSTO':>10}  {'VENTA':>10}")
            lb.insert(tk.END, f"  {'─'*50}")
            for costo, venta, fecha in historial:
                lb.insert(tk.END, f"  {fecha:<22}  ${costo:>9.2f}  ${venta:>9.2f}")

    def cancelar_edicion(self):
        self.limpiar_campos()
        self.desactivar_modo_edicion()

    def eliminar(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showerror("Error", "Seleccioná un producto")
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            return
        database.eliminar_producto(self.productos_cache[sel[0]][0])
        self.cargar_productos()

    def obtener_datos(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return (None,) * 4
        try:
            costo = float(self.entry_costo.get())
            venta = float(self.entry_venta.get())
            stock = int(self.entry_stock.get())
            if costo < 0 or venta < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Valores numéricos inválidos")
            return (None,) * 4
        return nombre, costo, venta, stock

    def limpiar_campos(self):
        for e in [self.entry_nombre, self.entry_costo, self.entry_venta, self.entry_stock]:
            e.delete(0, tk.END)

    def cargar_productos(self):
        self.lista.delete(0, tk.END)
        self.productos_cache = database.obtener_todos_productos()
        for p in self.productos_cache:
            ganancia = p[3] - p[2]
            margen = (ganancia / p[2] * 100) if p[2] > 0 else 0
            alerta = "  ⚠ STOCK BAJO" if p[4] <= 3 else ""
            self.lista.insert(
                tk.END,
                f"  {p[1]:<28}  C:${p[2]:<8.2f} V:${p[3]:<8.2f}  +{margen:.0f}%  Stock:{p[4]}{alerta}"
            )
            if p[4] <= 3:
                self.lista.itemconfig(tk.END, fg=theme.ACCENT2)
