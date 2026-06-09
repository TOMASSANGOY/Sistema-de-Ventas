import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from datetime import datetime
import database
import theme


class Historial:

    def __init__(self, parent):
        self.frame = theme.frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.ventas_cache = []

        # Título
        title_bar = theme.frame(self.frame, bg=theme.BG_CARD)
        title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        theme.label(title_bar, "📋  Historial de Ventas", style="title", bg=theme.BG_CARD).pack(side="left", padx=20, pady=14)

        # Barra de búsqueda
        bar = theme.card(self.frame, title=" Filtrar por fecha")
        bar.grid(row=0, column=0, sticky="ew", padx=12, pady=(60,0))

        inner = theme.frame(bar, bg=theme.BG_CARD)
        inner.pack(pady=8, padx=10, fill="x")

        theme.label(inner, "Fecha:", bg=theme.BG_CARD).pack(side="left", padx=(0,6))

        self.fecha_entry = DateEntry(
            inner, date_pattern="yyyy-mm-dd", width=12,
            background=theme.BG_CARD, foreground=theme.TEXT_MAIN,
            headersbackground=theme.ACCENT, headersforeground="white",
            selectbackground=theme.ACCENT,
            font=theme.FONT_BODY
        )
        self.fecha_entry.pack(side="left", padx=4)
        theme.btn_primary(inner, "Buscar", self.buscar_por_fecha).pack(side="left", padx=8)

        self.lbl_resumen = theme.label(inner, "", bg=theme.BG_CARD, fg=theme.TEXT_MUTED)
        self.lbl_resumen.pack(side="right", padx=10)

        # Lista
        list_card = theme.card(self.frame, title=" Ventas del día")
        list_card.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        list_card.rowconfigure(0, weight=1)
        list_card.columnconfigure(0, weight=1)

        lf, self.lista = theme.scrolled_listbox(list_card, width=100, height=22)
        lf.pack(fill="both", expand=True, padx=8, pady=8)
        self.lista.bind("<Double-Button-1>", self.ver_detalle)

        theme.label(list_card, "↵ Doble click para ver detalle", style="small",
                    bg=theme.BG_CARD, fg=theme.TEXT_MUTED).pack(anchor="e", padx=10, pady=(0,4))

        self.cargar_ventas()

    def buscar_por_fecha(self):
        self.cargar_ventas(self.fecha_entry.get())

    def cargar_ventas(self, fecha=None):
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
        self.lista.delete(0, tk.END)
        self.ventas_cache = database.obtener_historial_por_fecha(fecha)

        if not self.ventas_cache:
            self.lista.insert(tk.END, "  Sin ventas para esta fecha.")
            self.lbl_resumen.config(text="")
            return

        total_dia = sum(v[1] for v in self.ventas_cache)
        self.lbl_resumen.config(text=f"{len(self.ventas_cache)} ventas  |  Total: ${total_dia:.2f}")

        for v in self.ventas_cache:
            self.lista.insert(
                tk.END,
                f"  #{v[0]:<5}  {v[3][11:16]}   ${v[1]:<10.2f}  {v[2]}"
            )

    def ver_detalle(self, event=None):
        if not self.lista.curselection():
            return
        idx = self.lista.curselection()[0]
        if idx >= len(self.ventas_cache):
            return

        venta = self.ventas_cache[idx]
        items = database.obtener_detalle_venta(venta[0])

        win = tk.Toplevel(self.frame)
        win.title(f"Venta #{venta[0]}")
        win.geometry("480x380")
        win.configure(bg=theme.BG_PANEL)
        win.grab_set()

        theme.label(win, f"Venta #{venta[0]}", style="heading", bg=theme.BG_PANEL).pack(pady=12)

        txt = tk.Text(win, font=theme.FONT_MONO,
                      bg=theme.BG_CARD, fg=theme.TEXT_MAIN,
                      relief="flat", padx=14, pady=10,
                      width=58, height=14)
        txt.pack(padx=14, pady=4)

        txt.insert(tk.END, f"Fecha:   {venta[3]}\n")
        txt.insert(tk.END, f"Método:  {venta[2]}\n")
        txt.insert(tk.END, f"{'─'*46}\n")

        total = 0
        for nombre, cant, subtotal in items:
            txt.insert(tk.END, f"{nombre:<32} x{cant:<4} ${subtotal:.2f}\n")
            total += subtotal

        txt.insert(tk.END, f"{'─'*46}\n")
        txt.insert(tk.END, f"TOTAL: ${total:.2f}\n")
        txt.config(state="disabled")
