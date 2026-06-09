import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import database
import theme


class Ventas:

    def __init__(self, parent):
        self.frame = theme.frame(parent)
        self.carrito = []
        self.total = 0

        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # ── Título ──────────────────────────────────
        title_bar = theme.frame(self.frame, bg=theme.BG_CARD)
        title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        theme.label(title_bar, "🛒  Nueva Venta", style="title", bg=theme.BG_CARD).pack(side="left", padx=20, pady=14)

        # ── Panel izquierdo: búsqueda ────────────────
        left = theme.card(self.frame, title=" Buscar producto")
        left.grid(row=1, column=0, sticky="nsew", padx=12, pady=10)

        theme.label(left, "Escribí el nombre:", bg=theme.BG_CARD).pack(anchor="w", padx=10, pady=(10,2))
        self.buscador = theme.entry(left, width=36)
        self.buscador.pack(padx=10, pady=4)
        self.buscador.focus()
        self.buscador.bind("<KeyRelease>", self.buscar_producto)
        self.buscador.bind("<Down>", self.bajar_a_lista)

        lf, self.lista_productos = theme.scrolled_listbox(left, width=46, height=10)
        lf.pack(padx=10, pady=6, fill="both", expand=True)
        self.lista_productos.bind("<Return>", self.seleccionar_producto)
        self.lista_productos.bind("<Double-Button-1>", self.seleccionar_producto)

        # ── Panel derecho: carrito ───────────────────
        right = theme.card(self.frame, title=" Carrito")
        right.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)

        theme.label(right, "Productos seleccionados:", bg=theme.BG_CARD).pack(anchor="w", padx=10, pady=(10,2))
        rf, self.lista_carrito = theme.scrolled_listbox(right, width=46, height=10)
        rf.pack(padx=10, pady=6, fill="both", expand=True)

        theme.btn_danger(right, "✕  Quitar seleccionado", self.eliminar_del_carrito).pack(pady=4)
        theme.separator(right).pack(fill="x", padx=10, pady=6)

        self.label_total = theme.label(right, "Total: $0.00",
                                       style="title", bg=theme.BG_CARD, fg=theme.ACCENT)
        self.label_total.pack(pady=4)
        theme.btn_success(right, "  Cobrar  ", self.abrir_ventana_pago, width=20).pack(pady=8)

    # ─────────────────────────────────────────
    def buscar_producto(self, event=None):
        productos = database.buscar_productos(self.buscador.get())
        self.lista_productos.delete(0, tk.END)
        for p in productos:
            self.lista_productos.insert(tk.END, f"  {p[1]:<30}  ${p[2]:<10.2f}  Stock:{p[3]}")

    def bajar_a_lista(self, event):
        if self.lista_productos.size() > 0:
            self.lista_productos.focus()
            self.lista_productos.selection_set(0)

    def seleccionar_producto(self, event=None):
        if not self.lista_productos.curselection():
            return
        idx = self.lista_productos.curselection()[0]
        productos = database.buscar_productos(self.buscador.get())
        if idx >= len(productos):
            return
        p = productos[idx]
        self.pedir_cantidad(p[0], p[1], p[2], p[3])

    def pedir_cantidad(self, producto_id, nombre, precio, stock):
        win = tk.Toplevel(self.frame)
        win.title("Cantidad")
        win.geometry("280x180")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()

        theme.label(win, nombre, style="heading", bg=theme.BG_PANEL).pack(pady=(16,2))
        theme.label(win, f"Precio: ${precio:.2f}  |  Stock: {stock}",
                    bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack()

        entry_cant = theme.entry(win, width=14)
        entry_cant.pack(pady=10)
        entry_cant.focus()

        def confirmar(event=None):
            try:
                cantidad = int(entry_cant.get())
                if cantidad <= 0 or cantidad > stock:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", f"Cantidad inválida (máx: {stock})", parent=win)
                return
            for i, item in enumerate(self.carrito):
                if item[0] == producto_id:
                    nueva = item[3] + cantidad
                    if nueva > stock:
                        messagebox.showerror("Error", "Stock insuficiente", parent=win)
                        return
                    self.carrito[i] = (producto_id, nombre, precio, nueva, precio * nueva)
                    self.actualizar_carrito()
                    win.destroy()
                    self.buscador.focus()
                    return
            self.carrito.append((producto_id, nombre, precio, cantidad, precio * cantidad))
            self.actualizar_carrito()
            win.destroy()
            self.buscador.focus()

        entry_cant.bind("<Return>", confirmar)
        theme.btn_success(win, "Agregar al carrito", confirmar).pack(pady=4)

    def actualizar_carrito(self):
        self.lista_carrito.delete(0, tk.END)
        self.total = 0
        for item in self.carrito:
            self.lista_carrito.insert(tk.END, f"  {item[1]:<28} x{item[3]:<4}  ${item[4]:.2f}")
            self.total += item[4]
        self.label_total.config(text=f"Total: ${self.total:.2f}")

    def eliminar_del_carrito(self):
        if not self.lista_carrito.curselection():
            return
        self.carrito.pop(self.lista_carrito.curselection()[0])
        self.actualizar_carrito()

    # ─────────────────────────────────────────
    # VENTANA DE PAGO
    # ─────────────────────────────────────────
    def abrir_ventana_pago(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agregá productos antes de cobrar.")
            return

        win = tk.Toplevel(self.frame)
        win.title("Cobrar")
        win.geometry("400x640")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()
        win.resizable(False, False)

        total_bruto = self.total

        # ── Encabezado total ─────────────────────────
        theme.label(win, "Total a cobrar", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(pady=(18,0))
        lbl_bruto = theme.label(win, f"${total_bruto:.2f}", style="title",
                                bg=theme.BG_PANEL, fg=theme.ACCENT)
        lbl_bruto.pack()

        theme.separator(win).pack(fill="x", padx=20, pady=10)

        # ── Descuento ────────────────────────────────
        desc_card = theme.frame(win, bg=theme.BG_PANEL)
        desc_card.pack(fill="x", padx=20)

        # Tipo de descuento ($ o %)
        tipo_row = theme.frame(desc_card, bg=theme.BG_PANEL)
        tipo_row.pack(anchor="w")
        theme.label(tipo_row, "Descuento:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(side="left", padx=(0,10))
        var_tipo_desc = tk.StringVar(value="$")
        for val, txt in [("$", "  Monto $  "), ("%", "  Porcentaje %  ")]:
            tk.Radiobutton(
                tipo_row, text=txt, variable=var_tipo_desc, value=val,
                bg=theme.BG_PANEL, fg=theme.TEXT_MAIN,
                selectcolor=theme.BG_CARD, activebackground=theme.BG_PANEL,
                font=theme.FONT_BODY, cursor="hand2",
                command=lambda: recalcular()
            ).pack(side="left", padx=2)

        val_row = theme.frame(desc_card, bg=theme.BG_PANEL)
        val_row.pack(anchor="w", pady=(4,0))
        entry_desc = theme.entry(val_row, width=10)
        entry_desc.insert(0, "0")
        entry_desc.pack(side="left")
        theme.label(val_row, "  → Neto:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(side="left")
        lbl_neto = theme.label(val_row, f"  ${total_bruto:.2f}",
                               style="heading", bg=theme.BG_PANEL, fg=theme.SUCCESS)
        lbl_neto.pack(side="left")

        def get_descuento():
            try:
                v = float(entry_desc.get())
            except ValueError:
                return 0
            if var_tipo_desc.get() == "%":
                return round(total_bruto * v / 100, 2)
            return v

        def recalcular(*_):
            neto = max(0, total_bruto - get_descuento())
            lbl_neto.config(text=f"  ${neto:.2f}")
            # actualizar split si está activo
            if var_split.get():
                _refrescar_split(neto)

        entry_desc.bind("<KeyRelease>", recalcular)

        theme.separator(win).pack(fill="x", padx=20, pady=10)

        # ── Método de pago principal ─────────────────
        theme.label(win, "Método de pago", style="heading", bg=theme.BG_PANEL).pack(pady=(0,4))
        var_metodo = tk.StringVar(value="Efectivo")
        mf = theme.frame(win, bg=theme.BG_PANEL)
        mf.pack()
        for m in ["Efectivo", "Débito", "Transferencia"]:
            tk.Radiobutton(mf, text=m, variable=var_metodo, value=m,
                           bg=theme.BG_PANEL, fg=theme.TEXT_MAIN,
                           selectcolor=theme.BG_CARD, activebackground=theme.BG_PANEL,
                           font=theme.FONT_BODY, cursor="hand2").pack(side="left", padx=8)

        theme.separator(win).pack(fill="x", padx=20, pady=10)

        # ── Split de pago ────────────────────────────
        var_split = tk.BooleanVar(value=False)
        tk.Checkbutton(
            win, text="✂  Dividir pago en dos métodos",
            variable=var_split,
            bg=theme.BG_PANEL, fg=theme.TEXT_MUTED,
            selectcolor=theme.BG_CARD, activebackground=theme.BG_PANEL,
            font=theme.FONT_SMALL, cursor="hand2",
            command=lambda: _toggle_split()
        ).pack(anchor="w", padx=22)

        split_frame = theme.frame(win, bg=theme.BG_PANEL)

        # Segunda fila: método 2
        var_m2 = tk.StringVar(value="Transferencia")
        m2f = theme.frame(split_frame, bg=theme.BG_PANEL)
        m2f.pack(anchor="w", padx=4, pady=(6,2))
        theme.label(m2f, "2do método:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(side="left", padx=(0,6))
        for m in ["Efectivo", "Débito", "Transferencia"]:
            tk.Radiobutton(m2f, text=m, variable=var_m2, value=m,
                           bg=theme.BG_PANEL, fg=theme.TEXT_MAIN,
                           selectcolor=theme.BG_CARD, activebackground=theme.BG_PANEL,
                           font=theme.FONT_SMALL, cursor="hand2").pack(side="left", padx=3)

        # Montos
        amf = theme.frame(split_frame, bg=theme.BG_PANEL)
        amf.pack(anchor="w", padx=4, pady=4)
        theme.label(amf, "1ro $:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(side="left")
        entry_p1 = theme.entry(amf, width=9)
        entry_p1.insert(0, "0")
        entry_p1.pack(side="left", padx=4)
        theme.label(amf, "2do $:", bg=theme.BG_PANEL, fg=theme.TEXT_MUTED).pack(side="left")
        entry_p2 = theme.entry(amf, width=9)
        entry_p2.insert(0, "0")
        entry_p2.config(state="readonly")
        entry_p2.pack(side="left", padx=4)

        def _refrescar_split(neto):
            try:
                p1 = float(entry_p1.get())
            except ValueError:
                p1 = 0
            entry_p2.config(state="normal")
            entry_p2.delete(0, tk.END)
            entry_p2.insert(0, f"{max(0, neto - p1):.2f}")
            entry_p2.config(state="readonly")

        def _on_p1(*_):
            neto = max(0, total_bruto - get_descuento())
            _refrescar_split(neto)

        entry_p1.bind("<KeyRelease>", _on_p1)

        def _toggle_split():
            if var_split.get():
                split_frame.pack(fill="x", padx=18, pady=2)
                neto = max(0, total_bruto - get_descuento())
                entry_p1.delete(0, tk.END)
                entry_p1.insert(0, f"{neto:.2f}")
                entry_p2.config(state="normal")
                entry_p2.delete(0, tk.END)
                entry_p2.insert(0, "0.00")
                entry_p2.config(state="readonly")
            else:
                split_frame.pack_forget()

        theme.separator(win).pack(fill="x", padx=20, pady=10)

        # ── Botones finales ──────────────────────────
        def cobrar():
            desc = get_descuento()
            neto = max(0, total_bruto - desc)

            if var_split.get():
                try:
                    p1 = float(entry_p1.get())
                    p2 = float(entry_p2.get())
                except ValueError:
                    messagebox.showerror("Error", "Ingresá montos válidos para el split.", parent=win)
                    return
                if abs(p1 + p2 - neto) > 0.02:
                    messagebox.showerror("Error",
                        f"Los montos del split deben sumar ${neto:.2f}\n"
                        f"Actualmente suman ${p1+p2:.2f}", parent=win)
                    return
                pagos = [(var_metodo.get(), p1), (var_m2.get(), p2)]
                database.registrar_venta(self.carrito, descuento=desc, pagos_extra=pagos)
                metodo_txt = f"{var_metodo.get()} ${p1:.0f} + {var_m2.get()} ${p2:.0f}"
            else:
                database.registrar_venta(self.carrito, metodo=var_metodo.get(), descuento=desc)
                metodo_txt = var_metodo.get()

            carrito_snap = list(self.carrito)
            desc_val = float(entry_desc.get()) if entry_desc.get() else 0
            tipo_desc = var_tipo_desc.get()

            win.destroy()
            self._mostrar_exito(f"✓  Cobrado — {metodo_txt}  |  Neto: ${neto:.2f}")
            self._limpiar()

            # Ofrecer ticket
            if messagebox.askyesno("🖨  Ticket", "¿Imprimís ticket al cliente?"):
                self._mostrar_ticket(carrito_snap, neto, desc, tipo_desc, desc_val)

        theme.btn_success(win, "✔  Confirmar cobro", cobrar, width=28).pack(pady=4)
        theme.btn_warning(win, "📒  Fiado (Cuenta Corriente)",
                          lambda: self._seleccionar_cliente_fiado(win), width=28).pack(pady=3)
        theme.btn_danger(win, "✕  Cancelar", win.destroy, width=28).pack(pady=3)

    # ─────────────────────────────────────────
    # TICKET
    # ─────────────────────────────────────────
    def _mostrar_ticket(self, carrito, neto, desc_monto, tipo_desc, desc_val):
        win = tk.Toplevel(self.frame)
        win.title("Ticket")
        win.geometry("400x540")
        win.configure(bg="white")
        win.resizable(False, True)

        def L(text, **kw):
            tk.Label(win, text=text, bg="white", **kw).pack(fill="x", padx=28)

        L("KIOSCO", font=("Courier New", 18, "bold"), fg="#00897b")
        L("─" * 38, font=("Courier New", 9), fg="#ccc")
        L(datetime.now().strftime("%d/%m/%Y   %H:%M"),
          font=("Courier New", 9), fg="#888")
        L("─" * 38, font=("Courier New", 9), fg="#ccc")

        for item in carrito:
            nombre, cant, precio, total_item = item[1], item[3], item[2], item[4]
            L(f"{nombre[:26]:<26}  x{cant}", font=("Courier New", 9), fg="#111", anchor="w")
            L(f"  @ ${precio:.2f}  =  ${total_item:.2f}", font=("Courier New", 8), fg="#666", anchor="w")

        L("─" * 38, font=("Courier New", 9), fg="#ccc")

        bruto = sum(i[4] for i in carrito)
        L(f"{'Subtotal':<28}${bruto:>8.2f}", font=("Courier New", 9), fg="#444", anchor="w")

        if desc_monto > 0:
            tag = f"Desc.({desc_val:.0f}%)" if tipo_desc == "%" else "Descuento"
            L(f"{tag:<28}-${desc_monto:>7.2f}", font=("Courier New", 9), fg="#e53935", anchor="w")

        L("═" * 38, font=("Courier New", 9), fg="#ccc")
        L(f"{'TOTAL':<28}${neto:>8.2f}",
          font=("Courier New", 11, "bold"), fg="#00897b", anchor="w")
        L("═" * 38, font=("Courier New", 9), fg="#ccc")
        L("¡Gracias por su compra!", font=("Courier New", 9, "italic"), fg="#888")

        btn_row = tk.Frame(win, bg="white")
        btn_row.pack(pady=14)

        def imprimir():
            import sys, os, tempfile, subprocess
            lineas = [
                "           KIOSCO",
                "─" * 40,
                datetime.now().strftime("  %d/%m/%Y   %H:%M"),
                "─" * 40,
            ]
            for item in carrito:
                lineas.append(f"  {item[1][:26]:<26} x{item[3]}")
                lineas.append(f"    @ ${item[2]:.2f}  =  ${item[4]:.2f}")
            lineas.append("─" * 40)
            bruto2 = sum(i[4] for i in carrito)
            lineas.append(f"  {'Subtotal':<28}${bruto2:.2f}")
            if desc_monto > 0:
                tag2 = f"Desc({desc_val:.0f}%)" if tipo_desc == "%" else "Descuento"
                lineas.append(f"  {tag2:<28}-${desc_monto:.2f}")
            lineas += ["=" * 40, f"  {'TOTAL':<28}${neto:.2f}", "=" * 40,
                       "  ¡Gracias por su compra!"]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt",
                                             mode="w", encoding="utf-8")
            tmp.write("\n".join(lineas))
            tmp.close()
            if sys.platform == "win32":
                os.startfile(tmp.name, "print")
            else:
                subprocess.call(["lpr", tmp.name])

        tk.Button(btn_row, text="🖨  Imprimir", command=imprimir,
                  bg="#00bfa5", fg="black", font=("Segoe UI", 10),
                  padx=14, pady=6, cursor="hand2", relief="flat").pack(side="left", padx=6)
        tk.Button(btn_row, text="✕  Cerrar", command=win.destroy,
                  bg="#e53935", fg="white", font=("Segoe UI", 10),
                  padx=14, pady=6, cursor="hand2", relief="flat").pack(side="left", padx=6)

    # ─────────────────────────────────────────
    def _mostrar_exito(self, texto):
        lbl = tk.Label(self.frame, text=texto,
                       font=theme.FONT_HEADING, bg=theme.SUCCESS, fg=theme.BG_ROOT,
                       padx=20, pady=10)
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        lbl.after(2200, lbl.destroy)

    def _seleccionar_cliente_fiado(self, ventana_pago):
        clientes = database.obtener_clientes()
        if not clientes:
            messagebox.showerror("Sin clientes",
                "Primero registrá un cliente en la pestaña Clientes.")
            return

        win = tk.Toplevel(self.frame)
        win.title("Seleccionar Cliente")
        win.geometry("360x360")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()

        theme.label(win, "¿A quién se le fía?", style="heading", bg=theme.BG_PANEL).pack(pady=14)
        lf, lb = theme.scrolled_listbox(win, width=44, height=12)
        lf.pack(padx=14, pady=4, fill="both", expand=True)

        for c in clientes:
            deuda = database.obtener_deuda_cliente(c[0])
            txt = f"  (debe ${deuda:.0f})" if deuda > 0 else ""
            lb.insert(tk.END, f"  {c[1]}{txt}")

        def confirmar():
            if not lb.curselection():
                messagebox.showerror("Error", "Seleccioná un cliente.", parent=win)
                return
            cliente = clientes[lb.curselection()[0]]
            database.registrar_venta(self.carrito, fiado=True, cliente_id=cliente[0])
            self._mostrar_exito(f"✓  Fiado — {cliente[1]}  |  ${self.total:.2f}")
            self._limpiar()
            win.destroy()
            ventana_pago.destroy()

        theme.btn_warning(win, "Confirmar Fiado", confirmar, width=22).pack(pady=10)

    def _limpiar(self):
        self.carrito.clear()
        self.actualizar_carrito()
        self.buscador.delete(0, tk.END)
        self.lista_productos.delete(0, tk.END)
        self.buscador.focus()
