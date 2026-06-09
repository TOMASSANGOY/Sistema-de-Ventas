"""
Paleta y utilidades de diseño.
Colores de marca: verde agua (#00bfa5), negro (#0d1412), blanco (#f5faf9)
"""

import tkinter as tk

# ── Paleta de marca ─────────────────────────────────
BG_ROOT      = "#0d1412"   # negro profundo
BG_PANEL     = "#111c1a"   # negro suave
BG_CARD      = "#172421"   # negro con toque verde
ACCENT       = "#00bfa5"   # verde agua principal
ACCENT2      = "#f5a623"   # naranja: alertas / fiados
SUCCESS      = "#00bfa5"   # verde agua: confirmaciones
DANGER       = "#e53935"   # rojo: eliminar / deuda
INFO         = "#0288d1"   # azul: edición
TEXT_MAIN    = "#f5faf9"   # blanco suave
TEXT_MUTED   = "#5e8c84"   # verde agua apagado
BORDER       = "#1e3530"   # borde oscuro

# ── Fuentes ─────────────────────────────────────────
FONT_TITLE   = ("Segoe UI", 18, "bold")
FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_BODY    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 10)

# ── Botones ──────────────────────────────────────────
def btn_primary(master, text, command, **kw):
    return _btn(master, text, command, ACCENT, BG_ROOT, **kw)

def btn_success(master, text, command, **kw):
    return _btn(master, text, command, ACCENT, BG_ROOT, **kw)

def btn_danger(master, text, command, **kw):
    return _btn(master, text, command, DANGER, TEXT_MAIN, **kw)

def btn_info(master, text, command, **kw):
    return _btn(master, text, command, INFO, TEXT_MAIN, **kw)

def btn_warning(master, text, command, **kw):
    return _btn(master, text, command, ACCENT2, BG_ROOT, **kw)

def btn_ghost(master, text, command, **kw):
    return _btn(master, text, command, BG_CARD, TEXT_MAIN, relief="flat", **kw)

def _btn(master, text, command, bg, fg, relief="flat", **kw):
    b = _Btn(master, text=text, command=command,
             bg=bg, fg=fg, relief=relief,
             font=FONT_BODY, cursor="hand2",
             padx=14, pady=6, bd=0, **kw)
    b._bg = bg
    b.bind("<Enter>", lambda e: b.config(bg=_lighten(bg)))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def _lighten(hex_color):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    r = min(255, r + 25)
    g = min(255, g + 25)
    b = min(255, b + 25)
    return f"#{r:02x}{g:02x}{b:02x}"

class _Btn(tk.Button):
    pass

def label(master, text, style="body", **kw):
    fonts = {"title": FONT_TITLE, "heading": FONT_HEADING,
             "body": FONT_BODY, "small": FONT_SMALL, "mono": FONT_MONO}
    return tk.Label(master, text=text, font=fonts.get(style, FONT_BODY),
                    bg=kw.pop("bg", BG_PANEL), fg=kw.pop("fg", TEXT_MAIN), **kw)

def entry(master, width=28, **kw):
    e = tk.Entry(master, width=width, font=FONT_BODY,
                 bg="#1a2e2a",
                 fg=TEXT_MAIN,
                 insertbackground=ACCENT,
                 relief="solid", bd=1,
                 highlightthickness=2,
                 highlightcolor=ACCENT,
                 highlightbackground=BORDER,
                 **kw)
    return e

def frame(master, **kw):
    return tk.Frame(master, bg=kw.pop("bg", BG_PANEL), **kw)

def card(master, title=None, **kw):
    return tk.LabelFrame(master, bg=BG_CARD, fg=TEXT_MUTED,
                         font=FONT_SMALL, relief="flat", bd=1,
                         text=title or "", **kw)

def listbox(master, **kw):
    return tk.Listbox(master,
                      bg=BG_CARD, fg=TEXT_MAIN,
                      selectbackground=ACCENT,
                      selectforeground=BG_ROOT,
                      font=FONT_MONO,
                      relief="flat", bd=0,
                      activestyle="none",
                      **kw)

def scrolled_listbox(master, **kw):
    f = frame(master)
    lb = listbox(f, **kw)
    sb = tk.Scrollbar(f, orient="vertical", command=lb.yview,
                      bg=BG_PANEL, troughcolor=BG_CARD)
    lb.config(yscrollcommand=sb.set)
    lb.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return f, lb

def separator(master):
    return tk.Frame(master, bg=BORDER, height=1)

def apply_ttk_style():
    import tkinter.ttk as ttk
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TNotebook",        background=BG_ROOT,  borderwidth=0)
    style.configure("TNotebook.Tab",    background=BG_PANEL, foreground=TEXT_MUTED,
                    font=FONT_BODY,     padding=[16, 8])
    style.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", ACCENT)])

    style.configure("Treeview",
                    background=BG_CARD, foreground=TEXT_MAIN,
                    fieldbackground=BG_CARD, rowheight=26,
                    font=FONT_BODY, borderwidth=0)
    style.configure("Treeview.Heading",
                    background=BG_PANEL, foreground=TEXT_MUTED,
                    font=FONT_SMALL, relief="flat")
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", BG_ROOT)])

    style.configure("TCombobox",
                    fieldbackground=BG_CARD, background=BG_CARD,
                    foreground=TEXT_MAIN,    selectbackground=ACCENT)
    style.configure("TScrollbar",
                    background=BG_PANEL, troughcolor=BG_CARD)
