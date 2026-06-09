import sqlite3
from datetime import datetime

DB_NAME = "kiosco.db"


def conectar():
    return sqlite3.connect(DB_NAME)


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────

def crear_tablas():
    with conectar() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre       TEXT    NOT NULL,
                precio_costo REAL    NOT NULL,
                precio_venta REAL    NOT NULL,
                stock        INTEGER NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                total       REAL    NOT NULL,
                metodo_pago TEXT    NOT NULL,
                fecha       TEXT    NOT NULL,
                cliente_id  INTEGER
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id    INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad    INTEGER NOT NULL,
                subtotal    REAL    NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT,
                telefono  TEXT,
                direccion TEXT,
                email     TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS fiados (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id  INTEGER NOT NULL,
                monto       REAL    NOT NULL,
                fecha       TEXT    NOT NULL,
                pagado      INTEGER DEFAULT 0,
                fecha_pago  TEXT,
                metodo_pago TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS detalle_fiado (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fiado_id    INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad    INTEGER NOT NULL,
                subtotal    REAL    NOT NULL
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS pagos_cc (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                monto      REAL    NOT NULL,
                fecha      TEXT    NOT NULL,
                metodo     TEXT
            )
        """)

        # Egresos: retiros de caja y pagos a proveedores
        c.execute("""
            CREATE TABLE IF NOT EXISTS egresos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo        TEXT    NOT NULL,
                descripcion TEXT,
                monto       REAL    NOT NULL,
                fecha       TEXT    NOT NULL,
                metodo      TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS historial_precios (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id     INTEGER NOT NULL,
                precio_costo    REAL    NOT NULL,
                precio_venta    REAL    NOT NULL,
                fecha           TEXT    NOT NULL
            )
        """)

        _migrar(c)
        conn.commit()


def _migrar(cursor):
    """Agrega columnas/tablas nuevas sin romper datos existentes."""
    cols_ventas = {r[1] for r in cursor.execute("PRAGMA table_info(ventas)")}
    if "cliente_id" not in cols_ventas:
        cursor.execute("ALTER TABLE ventas ADD COLUMN cliente_id INTEGER")

    cols_fiados = {r[1] for r in cursor.execute("PRAGMA table_info(fiados)")}
    for col, tipo in [("fecha_pago", "TEXT"), ("metodo_pago", "TEXT")]:
        if col not in cols_fiados:
            cursor.execute(f"ALTER TABLE fiados ADD COLUMN {col} {tipo}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_fiado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiado_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagos_cc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            metodo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS egresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            descripcion TEXT,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            metodo TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_precios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id     INTEGER NOT NULL,
            precio_costo    REAL    NOT NULL,
            precio_venta    REAL    NOT NULL,
            fecha           TEXT    NOT NULL
        )
    """)


# ─────────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────────

def agregar_producto(nombre, costo, venta, stock):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO productos (nombre, precio_costo, precio_venta, stock) VALUES (?,?,?,?)",
            (nombre, costo, venta, stock)
        )

def editar_producto(producto_id, nombre, costo, venta, stock):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conn:
        # Guardar en historial si cambiaron los precios
        row = conn.execute(
            "SELECT precio_costo, precio_venta FROM productos WHERE id=?", (producto_id,)
        ).fetchone()
        if row and (row[0] != costo or row[1] != venta):
            conn.execute(
                "INSERT INTO historial_precios (producto_id, precio_costo, precio_venta, fecha) VALUES (?,?,?,?)",
                (producto_id, costo, venta, fecha)
            )
        conn.execute(
            "UPDATE productos SET nombre=?, precio_costo=?, precio_venta=?, stock=? WHERE id=?",
            (nombre, costo, venta, stock, producto_id)
        )

def obtener_historial_precios(producto_id):
    with conectar() as conn:
        return conn.execute(
            "SELECT precio_costo, precio_venta, fecha FROM historial_precios WHERE producto_id=? ORDER BY fecha DESC",
            (producto_id,)
        ).fetchall()

def eliminar_producto(producto_id):
    with conectar() as conn:
        conn.execute("DELETE FROM productos WHERE id=?", (producto_id,))

def obtener_todos_productos():
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nombre, precio_costo, precio_venta, stock FROM productos ORDER BY nombre"
        ).fetchall()

def buscar_productos(texto):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nombre, precio_venta, stock FROM productos WHERE nombre LIKE ?",
            (f"%{texto}%",)
        ).fetchall()


# ─────────────────────────────────────────────
# VENTAS
# ─────────────────────────────────────────────

def registrar_venta(carrito, metodo="Efectivo", cliente_id=None, fiado=False, descuento=0, pagos_extra=None):
    """
    fiado=True      → descuenta stock, anota deuda. NO entra a caja.
    fiado=False     → descuenta stock, registra en ventas (caja).
    descuento       → monto a descontar del total.
    pagos_extra     → lista de (metodo, monto) para split de pago. Si se pasa, ignora metodo.
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_bruto = sum(item[4] for item in carrito)
    total = max(0, total_bruto - descuento)

    with conectar() as conn:
        c = conn.cursor()
        for item in carrito:
            c.execute(
                "UPDATE productos SET stock = stock - ? WHERE id = ?",
                (item[3], item[0])
            )

        if fiado and cliente_id:
            c.execute(
                "INSERT INTO fiados (cliente_id, monto, fecha) VALUES (?,?,?)",
                (cliente_id, total, fecha)
            )
            fiado_id = c.lastrowid
            for item in carrito:
                c.execute(
                    "INSERT INTO detalle_fiado (fiado_id, producto_id, cantidad, subtotal) VALUES (?,?,?,?)",
                    (fiado_id, item[0], item[3], item[4])
                )
        else:
            if pagos_extra:
                # Múltiples métodos: una fila en ventas por cada método
                metodos_str = "+".join(f"{m}({v:.0f})" for m, v in pagos_extra)
                for pago_metodo, pago_monto in pagos_extra:
                    c.execute(
                        "INSERT INTO ventas (total, metodo_pago, fecha, cliente_id) VALUES (?,?,?,?)",
                        (pago_monto, pago_metodo, fecha, cliente_id)
                    )
                    venta_id = c.lastrowid
                    # solo adjuntar detalle a la primera fila
                venta_id_principal = c.execute(
                    "SELECT id FROM ventas WHERE fecha=? AND cliente_id IS ? ORDER BY id LIMIT 1",
                    (fecha, cliente_id)
                ).fetchone()[0]
                for item in carrito:
                    c.execute(
                        "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal) VALUES (?,?,?,?)",
                        (venta_id_principal, item[0], item[3], item[4])
                    )
            else:
                c.execute(
                    "INSERT INTO ventas (total, metodo_pago, fecha, cliente_id) VALUES (?,?,?,?)",
                    (total, metodo, fecha, cliente_id)
                )
                venta_id = c.lastrowid
                for item in carrito:
                    c.execute(
                        "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal) VALUES (?,?,?,?)",
                        (venta_id, item[0], item[3], item[4])
                    )
        conn.commit()


def cobrar_fiado(fiado_id, metodo):
    """Marca fiado como pagado y recién ahí lo mete en caja."""
    with conectar() as conn:
        c = conn.cursor()
        fecha_pago = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        row = c.execute(
            "SELECT cliente_id, monto FROM fiados WHERE id=?", (fiado_id,)
        ).fetchone()
        if not row:
            return
        cliente_id, monto = row

        c.execute(
            "UPDATE fiados SET pagado=1, fecha_pago=?, metodo_pago=? WHERE id=?",
            (fecha_pago, metodo, fiado_id)
        )
        c.execute(
            "INSERT INTO ventas (total, metodo_pago, fecha, cliente_id) VALUES (?,?,?,?)",
            (monto, metodo, fecha_pago, cliente_id)
        )
        venta_id = c.lastrowid

        items = c.execute(
            "SELECT producto_id, cantidad, subtotal FROM detalle_fiado WHERE fiado_id=?",
            (fiado_id,)
        ).fetchall()
        for producto_id, cantidad, subtotal in items:
            c.execute(
                "INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal) VALUES (?,?,?,?)",
                (venta_id, producto_id, cantidad, subtotal)
            )
        conn.commit()


def obtener_ventas():
    with conectar() as conn:
        return conn.execute(
            "SELECT id, fecha, total, metodo_pago FROM ventas ORDER BY id DESC"
        ).fetchall()

def obtener_historial_por_fecha(fecha):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, total, metodo_pago, fecha FROM ventas WHERE date(fecha)=? ORDER BY fecha DESC",
            (fecha,)
        ).fetchall()

def obtener_detalle_venta(venta_id):
    with conectar() as conn:
        return conn.execute("""
            SELECT p.nombre, d.cantidad, d.subtotal
            FROM detalle_venta d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.venta_id = ?
        """, (venta_id,)).fetchall()


# ─────────────────────────────────────────────
# CLIENTES
# ─────────────────────────────────────────────

def agregar_cliente(nombre, telefono=None, direccion=None, email=None):
    with conectar() as conn:
        conn.execute(
            "INSERT INTO clientes (nombre, telefono, direccion, email) VALUES (?,?,?,?)",
            (nombre, telefono, direccion, email)
        )

def editar_cliente(cliente_id, nombre, telefono=None, direccion=None, email=None):
    with conectar() as conn:
        conn.execute(
            "UPDATE clientes SET nombre=?, telefono=?, direccion=?, email=? WHERE id=?",
            (nombre, telefono, direccion, email, cliente_id)
        )

def eliminar_cliente(cliente_id):
    with conectar() as conn:
        conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))

def obtener_clientes():
    with conectar() as conn:
        return conn.execute(
            "SELECT id, nombre, telefono, direccion, email FROM clientes ORDER BY nombre"
        ).fetchall()


# ─────────────────────────────────────────────
# FIADOS / CUENTA CORRIENTE
# ─────────────────────────────────────────────

def obtener_todos_fiados_cliente(cliente_id):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, monto, fecha, pagado, fecha_pago, metodo_pago FROM fiados WHERE cliente_id=? ORDER BY fecha DESC",
            (cliente_id,)
        ).fetchall()

def obtener_detalle_fiado(fiado_id):
    with conectar() as conn:
        return conn.execute("""
            SELECT p.nombre, d.cantidad, d.subtotal
            FROM detalle_fiado d
            JOIN productos p ON d.producto_id = p.id
            WHERE d.fiado_id = ?
        """, (fiado_id,)).fetchall()

def obtener_deuda_cliente(cliente_id):
    with conectar() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(monto), 0) FROM fiados WHERE cliente_id=? AND pagado=0",
            (cliente_id,)
        ).fetchone()
        return row[0] if row else 0

def obtener_resumen_deudas():
    with conectar() as conn:
        return conn.execute("""
            SELECT c.id, c.nombre, COALESCE(SUM(f.monto), 0) AS deuda
            FROM clientes c
            LEFT JOIN fiados f ON f.cliente_id = c.id AND f.pagado = 0
            GROUP BY c.id
            ORDER BY deuda DESC
        """).fetchall()


# ─────────────────────────────────────────────
# EGRESOS (retiros / proveedores)
# ─────────────────────────────────────────────

def registrar_egreso(tipo, descripcion, monto, metodo="Efectivo"):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conectar() as conn:
        conn.execute(
            "INSERT INTO egresos (tipo, descripcion, monto, fecha, metodo) VALUES (?,?,?,?,?)",
            (tipo, descripcion, monto, fecha, metodo)
        )

def obtener_egresos_por_fecha(fecha):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, tipo, descripcion, monto, metodo, fecha FROM egresos WHERE date(fecha)=? ORDER BY fecha DESC",
            (fecha,)
        ).fetchall()

def obtener_egresos_por_mes(mes):
    with conectar() as conn:
        return conn.execute(
            "SELECT id, tipo, descripcion, monto, metodo, fecha FROM egresos WHERE substr(fecha,1,7)=? ORDER BY fecha DESC",
            (mes,)
        ).fetchall()

def obtener_balance_dia(fecha):
    """Ingresos (ventas) - Egresos del día."""
    with conectar() as conn:
        ingresos = conn.execute(
            "SELECT COALESCE(SUM(total),0) FROM ventas WHERE date(fecha)=?", (fecha,)
        ).fetchone()[0]
        egresos = conn.execute(
            "SELECT COALESCE(SUM(monto),0) FROM egresos WHERE date(fecha)=?", (fecha,)
        ).fetchone()[0]
    return ingresos, egresos, ingresos - egresos
