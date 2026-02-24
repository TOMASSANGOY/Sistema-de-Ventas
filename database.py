import sqlite3
from datetime import datetime

DB_NAME = "kiosco.db"

def conectar():
    return sqlite3.connect(DB_NAME)


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    # ================= PRODUCTOS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio_costo REAL NOT NULL,
        precio_venta REAL NOT NULL,
        stock INTEGER NOT NULL
    )
    """)

    # ================= VENTAS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        metodo_pago TEXT NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detalle_venta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad INTEGER,
        subtotal REAL
    )
    """)

    # ================= CLIENTES =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT
    )
    """)
    # agregar columnas nuevas si no existen
    columnas = [col[1] for col in cursor.execute("PRAGMA table_info(clientes)")]
    if "telefono" not in columnas:
        cursor.execute("ALTER TABLE clientes ADD COLUMN telefono TEXT")
    if "direccion" not in columnas:
        cursor.execute("ALTER TABLE clientes ADD COLUMN direccion TEXT")
    if "email" not in columnas:
        cursor.execute("ALTER TABLE clientes ADD COLUMN email TEXT")

    # ================= FIADOS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fiados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER,
        monto REAL,
        fecha TEXT,
        pagado INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# ================= PRODUCTOS =================

def agregar_producto(nombre, costo, venta, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, precio_costo, precio_venta, stock)
        VALUES (?, ?, ?, ?)
    """, (nombre, costo, venta, stock))
    conn.commit()
    conn.close()


def editar_producto(producto_id, nombre, costo, venta, stock):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre=?, precio_costo=?, precio_venta=?, stock=?
        WHERE id=?
    """, (nombre, costo, venta, stock, producto_id))
    conn.commit()
    conn.close()


def eliminar_producto(producto_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
    conn.commit()
    conn.close()


def obtener_todos_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio_costo, precio_venta, stock FROM productos")
    datos = cursor.fetchall()
    conn.close()
    return datos


def buscar_productos(texto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, precio_venta, stock
        FROM productos
        WHERE nombre LIKE ?
    """, (f"%{texto}%",))
    datos = cursor.fetchall()
    conn.close()
    return datos


# ================= VENTAS =================

def registrar_venta(carrito, metodo="Efectivo", cliente_id=None, fiado=False):

    conn = conectar()
    cursor = conn.cursor()

    total = sum(item[4] for item in carrito)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ===============================
    # SI ES FIADO
    # ===============================
    if fiado and cliente_id:

        # descontar stock
        for item in carrito:
            producto_id = item[0]
            cantidad = item[3]

            cursor.execute("""
                UPDATE productos
                SET stock = stock - ?
                WHERE id = ?
            """, (cantidad, producto_id))

        # guardar deuda
        cursor.execute("""
            INSERT INTO fiados (cliente_id, monto, fecha, pagado)
            VALUES (?, ?, ?, 0)
        """, (cliente_id, total, fecha))

        conn.commit()
        conn.close()
        return

    # ===============================
    # SI ES VENTA NORMAL
    # ===============================

    cursor.execute("""
        INSERT INTO ventas (total, metodo_pago, fecha)
        VALUES (?, ?, ?)
    """, (total, metodo, fecha))

    venta_id = cursor.lastrowid

    for item in carrito:
        producto_id = item[0]
        cantidad = item[3]
        subtotal = item[4]

        cursor.execute("""
            INSERT INTO detalle_venta (venta_id, producto_id, cantidad, subtotal)
            VALUES (?, ?, ?, ?)
        """, (venta_id, producto_id, cantidad, subtotal))

        cursor.execute("""
            UPDATE productos
            SET stock = stock - ?
            WHERE id = ?
        """, (cantidad, producto_id))

    conn.commit()
    conn.close()


def obtener_ventas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha, total, metodo_pago
        FROM ventas
        ORDER BY id DESC
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_detalle_venta(venta_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.nombre, d.cantidad, d.subtotal
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        WHERE d.venta_id = ?
    """, (venta_id,))
    datos = cursor.fetchall()
    conn.close()
    return datos


# ================= CLIENTES =================

def agregar_cliente(nombre=None, telefono=None, direccion=None, email=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (nombre, telefono, direccion, email)
        VALUES (?, ?, ?, ?)
    """, (nombre, telefono, direccion, email))
    conn.commit()
    conn.close()


def editar_cliente(cliente_id, nombre=None, telefono=None, direccion=None, email=None):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nombre=?, telefono=?, direccion=?, email=?
        WHERE id=?
    """, (nombre, telefono, direccion, email, cliente_id))
    conn.commit()
    conn.close()


def eliminar_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()


def obtener_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, direccion, email FROM clientes")
    datos = cursor.fetchall()
    conn.close()
    return datos


# ================= FIADOS =================

def obtener_fiados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, c.nombre, f.monto, f.fecha, f.pagado
        FROM fiados f
        JOIN clientes c ON f.cliente_id = c.id
        ORDER BY f.pagado, f.fecha DESC
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos


def pagar_fiado(fiado_id, metodo_pago="Efectivo"):

    conn = conectar()
    cursor = conn.cursor()

    # Obtener datos del fiado
    cursor.execute("""
        SELECT cliente_id, monto
        FROM fiados
        WHERE id = ?
    """, (fiado_id,))

    fiado = cursor.fetchone()

    if not fiado:
        conn.close()
        return

    cliente_id, monto = fiado
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Registrar ingreso real en ventas
    cursor.execute("""
        INSERT INTO ventas (total, metodo_pago, fecha)
        VALUES (?, ?, ?)
    """, (monto, metodo_pago, fecha))

    # Marcar fiado como pagado
    cursor.execute("""
        UPDATE fiados
        SET pagado = 1
        WHERE id = ?
    """, (fiado_id,))

    conn.commit()
    conn.close()

# ================= CONTABILIDAD =================

def obtener_caja_del_dia():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(total), 0), COUNT(*)
        FROM ventas
        WHERE strftime('%Y-%m-%d', fecha) = strftime('%Y-%m-%d', 'now', 'localtime')
    """)
    total_dia, cantidad_ventas = cursor.fetchone()

    cursor.execute("""
        SELECT metodo_pago, IFNULL(SUM(total), 0)
        FROM ventas
        WHERE strftime('%Y-%m-%d', fecha) = strftime('%Y-%m-%d', 'now', 'localtime')
        GROUP BY metodo_pago
    """)
    metodos = cursor.fetchall()

    cursor.execute("""
        SELECT IFNULL(SUM(d.subtotal - (p.precio_costo * d.cantidad)), 0)
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        JOIN ventas v ON d.venta_id = v.id
        WHERE strftime('%Y-%m-%d', v.fecha) = strftime('%Y-%m-%d', 'now', 'localtime')
    """)
    ganancia = cursor.fetchone()[0]

    conn.close()
    return total_dia, cantidad_ventas, metodos, ganancia


def obtener_ganancia_del_mes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(total), 0), COUNT(*)
        FROM ventas
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    """)
    total_mes, cantidad_ventas = cursor.fetchone()

    cursor.execute("""
        SELECT IFNULL(SUM(d.subtotal - (p.precio_costo * d.cantidad)), 0)
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        JOIN ventas v ON d.venta_id = v.id
        WHERE strftime('%Y-%m', v.fecha) = strftime('%Y-%m', 'now')
    """)
    ganancia_mes = cursor.fetchone()[0]

    conn.close()
    return total_mes, cantidad_ventas, ganancia_mes


# ================= HISTORIAL =================

def obtener_historial_por_fecha(fecha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, total, metodo_pago, fecha
        FROM ventas
        WHERE strftime('%Y-%m-%d', fecha) = ?
        ORDER BY fecha DESC
    """, (fecha,))
    ventas = cursor.fetchall()
    conn.close()
    return ventas


def obtener_caja_por_fecha(fecha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(total), 0), COUNT(*)
        FROM ventas
        WHERE strftime('%Y-%m-%d', fecha) = ?
    """, (fecha,))
    total, cantidad = cursor.fetchone()

    cursor.execute("""
        SELECT metodo_pago, IFNULL(SUM(total), 0)
        FROM ventas
        WHERE strftime('%Y-%m-%d', fecha) = ?
        GROUP BY metodo_pago
    """, (fecha,))
    metodos = cursor.fetchall()

    cursor.execute("""
        SELECT IFNULL(SUM(d.subtotal - (p.precio_costo * d.cantidad)), 0)
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        JOIN ventas v ON d.venta_id = v.id
        WHERE strftime('%Y-%m-%d', v.fecha) = ?
    """, (fecha,))
    ganancia = cursor.fetchone()[0]

    conn.close()
    return total, cantidad, metodos, ganancia


def obtener_ganancia_por_mes(mes):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT IFNULL(SUM(total), 0), COUNT(*)
        FROM ventas
        WHERE strftime('%Y-%m', fecha) = ?
    """, (mes,))
    total, cantidad = cursor.fetchone()

    cursor.execute("""
        SELECT IFNULL(SUM(d.subtotal - (p.precio_costo * d.cantidad)), 0)
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        JOIN ventas v ON d.venta_id = v.id
        WHERE strftime('%Y-%m', v.fecha) = ?
    """, (mes,))
    ganancia = cursor.fetchone()[0]

    conn.close()
    return total, cantidad, ganancia