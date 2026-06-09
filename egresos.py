import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import database
import theme


TIPOS = ["Retiro de caja", "Pago proveedor", "Gasto operativo", "Otro"]
METODOS = ["Efectivo", "Débito", "Transferencia"]


class Egresos:

    def __init__(self, parent):
        self.frame = theme.frame(parent)
        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # Título
        title_bar = theme.frame(self.frame, bg=theme.BG_CARD)
        title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        theme.label(title_bar, "💸  Egresos de Caja", style="title", bg=theme.BG_CARD).pack(side="left", padx=20, pady=14)

        # ── Formulario ───────────────────────────────
        form = theme.card(self.frame, title=" Registrar egreso")
        form.grid(row=1, column=0, sticky="ns", padx=12, pady=10)

        theme.label(form, "Tipo", bg=theme.BG_CARD).pack(anchor="w", padx=12, pady=(10,0))
        self.var_tipo = tk.StringVar(value=TIPOS[0])
        for t in TIPOS:
            rb = tk.Radiobutton(
                form, text=t, variable=self.var_tipo, value=t,
                bg=theme.BG_CARD, fg=theme.TEXT_MAIN,
                selectcolor=theme.BG_PANEL,
                activebackground=theme.BG_CARD,
                font=theme.FONT_BODY, cursor="hand2"
            )
            rb.pack(anchor="w", padx=16, pady=1)

        theme.separator(form).pack(fill="x", padx=12, pady=8)

        theme.label(form, "Descripción / detalle", bg=theme.BG_CARD).pack(anchor="w", padx=12)
        self.entry_desc = theme.entry(form, width=24)
        self.entry_desc.pack(padx=12, pady=4)

        theme.label(form, "Monto ($)", bg=theme.BG_CARD).pack(anchor="w", padx=12)
        self.entry_monto = theme.entry(form, width=14)
        self.entry_monto.pack(padx=12, pady=4)

        theme.label(form, "Método de pago", bg=theme.BG_CARD).pack(anchor="w", padx=12)
        self.var_metodo = tk.StringVar(value=METODOS[0])
        metodo_frame = theme.frame(form, bg=theme.BG_CARD)
        metodo_frame.pack(anchor="w", padx=12, pady=4)
        for m in METODOS:
            tk.Radiobutton(
                metodo_frame, text=m, variable=self.var_metodo, value=m,
                bg=theme.BG_CARD, fg=theme.TEXT_MAIN,
                selectcolor=theme.BG_PANEL,
                activebackground=theme.BG_CARD,
                font=theme.FONT_BODY, cursor="hand2"
            ).pack(side="left", padx=6)

        theme.separator(form).pack(fill="x", padx=12, pady=8)
        theme.btn_danger(form, "💸  Registrar Egreso", self.registrar, width=22).pack(pady=6)

        # ── Panel derecho: historial ─────────────────
        right = theme.frame(self.frame)
        right.grid(row=1, column=1, sticky="nsew", padx=12, pady=10)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        # Filtro fecha
        filter_bar = theme.card(right, title=" Ver por fecha")
        filter_bar.grid(row=0, column=0, sticky="ew", pady=(0,8))

        inner = theme.frame(filter_bar, bg=theme.BG_CARD)
        inner.pack(pady=8, padx=10)

        theme.label(inner, "Fecha:", bg=theme.BG_CARD).pack(side="left", padx=(0,6))
        self.fecha_entry = DateEntry(
            inner, date_pattern="yyyy-mm-dd", width=12,
            background=theme.BG_CARD, foreground=theme.TEXT_MAIN,
            headersbackground=theme.ACCENT, headersforeground="white",
            selectbackground=theme.ACCENT,
            font=theme.FONT_BODY
        )
        self.fecha_entry.pack(side="left", padx=4)
        theme.btn_primary(inner, "Buscar", self.cargar_historial).pack(side="left", padx=8)

        self.lbl_total = theme.label(inner, "", bg=theme.BG_CARD, fg=theme.ACCENT)
        self.lbl_total.pack(side="right", padx=10)

        # Lista egresos
        list_card = theme.card(right, title=" Egresos registrados")
        list_card.grid(row=1, column=0, sticky="nsew")
        list_card.rowconfigure(0, weight=1)
        list_card.columnconfigure(0, weight=1)

        lf, self.lista = theme.scrolled_listbox(list_card, width=70, height=20)
        lf.pack(fill="both", expand=True, padx=8, pady=8)

        self.cargar_historial()

    def registrar(self):
        tipo  = self.var_tipo.get()
        desc  = self.entry_desc.get().strip()
        metodo = self.var_metodo.get()

        try:
            monto = float(self.entry_monto.get())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingresá un monto válido (mayor a 0)")
            return

        if not messagebox.askyesno(
            "Confirmar egreso",
            f"¿Registrar egreso?\n\nTipo:   {tipo}\nDetalle: {desc or '—'}\nMonto:  ${monto:.2f}\nMétodo: {metodo}"
        ):
            return

        database.registrar_egreso(tipo, desc, monto, metodo)
        messagebox.showinfo("✓ Registrado", f"Egreso de ${monto:.2f} registrado.")
        self.entry_desc.delete(0, tk.END)
        self.entry_monto.delete(0, tk.END)
        self.cargar_historial()

    def cargar_historial(self):
        fecha = self.fecha_entry.get()
        self.lista.delete(0, tk.END)
        egresos = database.obtener_egresos_por_fecha(fecha)

        if not egresos:
            self.lista.insert(tk.END, "  Sin egresos para esta fecha.")
            self.lbl_total.config(text="")
            return

        total = 0
        for eg in egresos:
            eid, tipo, desc, monto, metodo, fecha_eg = eg
            self.lista.insert(
                tk.END,
                f"  {fecha_eg[11:16]}  [{tipo}]  {(desc or ''):<24}  ${monto:.2f}  ({metodo})"
            )
            total += monto

        self.lbl_total.config(text=f"Total: ${total:.2f}")
