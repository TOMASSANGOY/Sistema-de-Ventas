import tkinter as tk
from tkinter import messagebox
import database
import theme


class Clientes:

    def __init__(self, parent):
        self.frame = theme.frame(parent)
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.cliente_editando_id = None
        self.clientes_cache = []
        self.fiados_cache = []

        # Título
        title_bar = theme.frame(self.frame, bg=theme.BG_CARD)
        title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        theme.label(title_bar, "👥  Clientes y Cuenta Corriente", style="title", bg=theme.BG_CARD).pack(side="left", padx=20, pady=14)

        # ── Formulario ───────────────────────────────
        form = theme.card(self.frame, title=" Datos del cliente")
        form.grid(row=1, column=0, sticky="ns", padx=12, pady=10)

        for label_txt, attr in [
            ("Nombre",    "entry_nombre"),
            ("Teléfono",  "entry_telefono"),
            ("Dirección", "entry_direccion"),
            ("Email",     "entry_email"),
        ]:
            theme.label(form, label_txt, bg=theme.BG_CARD).pack(anchor="w", padx=12, pady=(8,0))
            e = theme.entry(form, width=24)
            e.pack(padx=12, pady=2)
            setattr(self, attr, e)

        theme.separator(form).pack(fill="x", padx=12, pady=10)

        self.btn_agregar  = theme.btn_success(form, "＋  Agregar",           self.agregar,          width=20)
        self.btn_editar   = theme.btn_info   (form, "✎  Editar",             self.cargar_para_editar, width=20)
        self.btn_guardar  = theme.btn_success(form, "✔  Guardar cambios",    self.guardar_cambios,  width=20, state="disabled")
        self.btn_cancelar = theme.btn_warning(form, "✕  Cancelar",           self.cancelar_edicion, width=20, state="disabled")
        self.btn_eliminar = theme.btn_danger (form, "🗑  Eliminar",           self.eliminar,         width=20)
        for b in [self.btn_agregar, self.btn_editar, self.btn_guardar, self.btn_cancelar, self.btn_eliminar]:
            b.pack(pady=3)

        # ── Panel derecho: lista + cuenta corriente ──
        right = theme.frame(self.frame)
        right.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        right.rowconfigure(3, weight=2)

        theme.label(right, "Clientes registrados", style="heading").pack(anchor="w", pady=(0,4))
        lf, self.lista = theme.scrolled_listbox(right, width=65, height=8)
        lf.pack(fill="x")
        self.lista.bind("<<ListboxSelect>>", self.on_seleccion_cliente)

        theme.separator(right).pack(fill="x", pady=10)

        # Cuenta corriente
        cc_header = theme.frame(right)
        cc_header.pack(fill="x")
        theme.label(cc_header, "📒  Cuenta Corriente", style="heading").pack(side="left")
        self.lbl_deuda = theme.label(cc_header, "Deuda: $0.00",
                                     fg=theme.ACCENT, bg=theme.BG_PANEL)
        self.lbl_deuda.pack(side="right", padx=10)

        lf2, self.lista_fiados = theme.scrolled_listbox(right, width=65, height=9)
        lf2.pack(fill="both", expand=True, pady=(4,0))
        self.lista_fiados.bind("<Double-Button-1>", self.ver_detalle_fiado)

        btn_row = theme.frame(right)
        btn_row.pack(pady=8)
        theme.btn_ghost  (btn_row, "🔍 Ver detalle",      self.ver_detalle_fiado).pack(side="left", padx=6)
        theme.btn_success(btn_row, "💰 Cobrar fiado",     self.cobrar_fiado_seleccionado).pack(side="left", padx=6)

        self.cargar_clientes()

    # ─────────────────────────────────────────
    def _toast(self, texto, color=None):
        """Mensaje flotante que desaparece solo, sin popup."""
        lbl = tk.Label(
            self.frame, text=texto,
            font=theme.FONT_BODY,
            bg=color or theme.SUCCESS, fg="white",
            padx=16, pady=8
        )
        lbl.place(relx=0.5, rely=0.97, anchor="s")
        lbl.after(2000, lbl.destroy)

    # ─────────────────────────────────────────
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

    def agregar(self):
        datos = self.obtener_datos()
        if datos[0] is None:
            return
        database.agregar_cliente(*datos)
        self.limpiar_campos()
        self.cargar_clientes()

    def cargar_para_editar(self):
        sel = self.lista.curselection()
        if not sel:
            messagebox.showerror("Error", "Seleccioná un cliente")
            return
        c = self.clientes_cache[sel[0]]
        self.cliente_editando_id = c[0]
        for entry, val in zip(
            [self.entry_nombre, self.entry_telefono, self.entry_direccion, self.entry_email],
            c[1:]
        ):
            entry.delete(0, tk.END)
            entry.insert(0, val or "")
        self.activar_modo_edicion()

    def guardar_cambios(self):
        if not self.cliente_editando_id:
            return
        datos = self.obtener_datos()
        if datos[0] is None:
            return
        database.editar_cliente(self.cliente_editando_id, *datos)
        self.limpiar_campos()
        self.cargar_clientes()
        self.desactivar_modo_edicion()
        self._toast("✓  Cliente actualizado")

    def cancelar_edicion(self):
        self.limpiar_campos()
        self.desactivar_modo_edicion()

    def eliminar(self):
        sel = self.lista.curselection()
        if not sel:
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            return
        database.eliminar_cliente(self.clientes_cache[sel[0]][0])
        self.cargar_clientes()

    # ─────────────────────────────────────────
    # CUENTA CORRIENTE
    # ─────────────────────────────────────────
    def on_seleccion_cliente(self, event=None):
        sel = self.lista.curselection()
        if not sel:
            return
        self.cargar_fiados(self.clientes_cache[sel[0]][0])

    def cargar_fiados(self, cliente_id):
        self.lista_fiados.delete(0, tk.END)
        self.fiados_cache = database.obtener_todos_fiados_cliente(cliente_id)
        deuda = database.obtener_deuda_cliente(cliente_id)
        self.lbl_deuda.config(
            text=f"Deuda: ${deuda:.2f}",
            fg=theme.ACCENT if deuda > 0 else theme.SUCCESS
        )
        for f in self.fiados_cache:
            fiado_id, monto, fecha, pagado, fecha_pago, metodo_pago = f
            if pagado:
                icono = "✓"
                color = theme.TEXT_MUTED
                estado = f"Pagado {fecha_pago[:10] if fecha_pago else ''} ({metodo_pago or ''})"
            else:
                icono = "⏳"
                color = theme.ACCENT2
                estado = "PENDIENTE"
            self.lista_fiados.insert(
                tk.END,
                f"  {icono}  {fecha[:10]}   ${monto:.2f}   {estado}"
            )
            self.lista_fiados.itemconfig(tk.END, fg=color)

    def ver_detalle_fiado(self, event=None):
        sel = self.lista_fiados.curselection()
        if not sel:
            messagebox.showinfo("Info", "Seleccioná un fiado de la lista.")
            return
        fiado = self.fiados_cache[sel[0]]
        fiado_id, monto, fecha, pagado, fecha_pago, metodo_pago = fiado
        items = database.obtener_detalle_fiado(fiado_id)

        win = tk.Toplevel(self.frame)
        win.title(f"Detalle Fiado — {fecha[:10]}")
        win.geometry("440x360")
        win.configure(bg=theme.BG_PANEL)

        theme.label(win, f"Fiado del {fecha[:10]}", style="heading", bg=theme.BG_PANEL).pack(pady=12)

        txt = tk.Text(win, font=theme.FONT_MONO,
                      bg=theme.BG_CARD, fg=theme.TEXT_MAIN,
                      relief="flat", padx=12, pady=8,
                      width=52, height=12)
        txt.pack(padx=14, pady=4)

        for nombre, cant, subtotal in items:
            txt.insert(tk.END, f"{nombre:<30} x{cant:<4} ${subtotal:.2f}\n")
        txt.insert(tk.END, f"\n{'─'*44}\n")
        txt.insert(tk.END, f"TOTAL: ${monto:.2f}\n")
        if pagado:
            txt.insert(tk.END, f"✓ Pagado el {fecha_pago} en {metodo_pago}\n")
        else:
            txt.insert(tk.END, "Estado: PENDIENTE DE PAGO\n")
        txt.config(state="disabled")

        if not pagado:
            theme.btn_success(win, "💰 Cobrar este fiado",
                              lambda: self._cobrar_desde_detalle(fiado_id, win)).pack(pady=8)

    def _cobrar_desde_detalle(self, fiado_id, ventana_origen):
        sel = self.lista.curselection()
        def callback():
            ventana_origen.destroy()
            if sel:
                self.cargar_fiados(self.clientes_cache[sel[0]][0])
            self.cargar_clientes()
        self._abrir_cobro(fiado_id, callback=callback)

    def cobrar_fiado_seleccionado(self):
        sel_c = self.lista.curselection()
        if not sel_c:
            messagebox.showerror("Error", "Primero seleccioná un cliente de la lista de arriba.")
            return
        sel_f = self.lista_fiados.curselection()
        if not sel_f:
            # intentar seleccionar el primer fiado pendiente automáticamente
            for i, f in enumerate(self.fiados_cache):
                if not f[3]:  # pagado == 0
                    self.lista_fiados.selection_set(i)
                    sel_f = (i,)
                    break
        if not sel_f:
            messagebox.showinfo("Sin pendientes", "Este cliente no tiene fiados pendientes.")
            return
        fiado = self.fiados_cache[sel_f[0]]
        fiado_id, monto, fecha, pagado, *_ = fiado
        if pagado:
            messagebox.showinfo("Info", "Este fiado ya está pagado.")
            return
        cliente_id = self.clientes_cache[sel_c[0]][0]
        def callback():
            self.cargar_fiados(cliente_id)
            self.cargar_clientes()
            self._toast(f"✓  Fiado cobrado — ${monto:.2f} ingresó a caja")
        self._abrir_cobro(fiado_id, callback=callback)

    def _abrir_cobro(self, fiado_id, callback=None):
        with database.conectar() as conn:
            row = conn.execute("SELECT monto FROM fiados WHERE id=?", (fiado_id,)).fetchone()
        if not row:
            return
        monto = row[0]

        win = tk.Toplevel(self.frame)
        win.title("Cobrar Fiado")
        win.geometry("280x260")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()

        theme.label(win, "Cobrar fiado", style="heading", bg=theme.BG_PANEL).pack(pady=(16,4))
        theme.label(win, f"${monto:.2f}", style="title", bg=theme.BG_PANEL, fg=theme.ACCENT).pack()
        theme.label(win, "Método de pago:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(pady=(12,4))

        def confirmar(metodo):
            database.cobrar_fiado(fiado_id, metodo)
            win.destroy()
            if callback:
                callback()

        for metodo in ["Efectivo", "Débito", "Transferencia"]:
            theme.btn_ghost(win, metodo, lambda m=metodo: confirmar(m), width=18).pack(pady=3)

    # ─────────────────────────────────────────
    def obtener_datos(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre no puede estar vacío")
            return (None,) * 4
        return (
            nombre,
            self.entry_telefono.get().strip(),
            self.entry_direccion.get().strip(),
            self.entry_email.get().strip(),
        )

    def limpiar_campos(self):
        for e in [self.entry_nombre, self.entry_telefono, self.entry_direccion, self.entry_email]:
            e.delete(0, tk.END)

    def cargar_clientes(self):
        self.lista.delete(0, tk.END)
        self.lista_fiados.delete(0, tk.END)
        self.lbl_deuda.config(text="Deuda: $0.00", fg=theme.SUCCESS)
        self.clientes_cache = database.obtener_clientes()
        for c in self.clientes_cache:
            deuda = database.obtener_deuda_cliente(c[0])
            deuda_txt = f"  💰 ${deuda:.0f}" if deuda > 0 else ""
            self.lista.insert(tk.END, f"  {c[1]:<28} {c[2] or '':<16}{deuda_txt}")
            if deuda > 0:
                self.lista.itemconfig(tk.END, fg=theme.ACCENT2)
