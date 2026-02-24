import database
from datetime import datetime


# ================= PRODUCTOS =================

def agregar_producto(nombre, precio_costo, precio_venta, stock):
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos 
        (nombre, precio_costo, precio_venta, stock)
        VALUES (?, ?, ?, ?)
    """, (nombre, precio_costo, precio_venta, stock))

    conn.commit()
    conn.close()


def editar_producto(producto_id, nombre, precio_costo, precio_venta, stock):
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE productos
        SET nombre=?, precio_costo=?, precio_venta=?, stock=?
        WHERE id=?
    """, (nombre, precio_costo, precio_venta, stock, producto_id))

    conn.commit()
    conn.close()


def obtener_todos_productos():
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio_costo, precio_venta, stock 
        FROM productos
    """)

    productos = cursor.fetchall()
    conn.close()
    return productos


def obtener_producto_por_id(producto_id):
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio_costo, precio_venta, stock
        FROM productos
        WHERE id = ?
    """, (producto_id,))

    producto = cursor.fetchone()
    conn.close()
    return producto


def descontar_stock(producto_id, cantidad):
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE productos
        SET stock = stock - ?
        WHERE id = ?
    """, (cantidad, producto_id))

    conn.commit()
    conn.close()


# ================= VENTAS =================

def guardar_venta(total, metodo_pago, carrito):

    conn = database.conectar()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO ventas (fecha, total, metodo_pago)
        VALUES (?, ?, ?)
    """, (fecha, total, metodo_pago))

    venta_id = cursor.lastrowid

    for pid, datos in carrito.items():
        cursor.execute("""
            INSERT INTO detalle_venta
            (venta_id, producto_id, cantidad, subtotal)
            VALUES (?, ?, ?, ?)
        """, (
            venta_id,
            pid,
            datos["cantidad"],
            datos["precio"] * datos["cantidad"]
        ))

    conn.commit()
    conn.close()


def obtener_ventas():
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, fecha, total, metodo_pago
        FROM ventas
        ORDER BY id DESC
    """)

    ventas = cursor.fetchall()
    conn.close()
    return ventas


def obtener_detalle_venta(venta_id):
    conn = database.conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.nombre, d.cantidad, d.subtotal
        FROM detalle_venta d
        JOIN productos p ON d.producto_id = p.id
        WHERE d.venta_id = ?
    """, (venta_id,))

    detalles = cursor.fetchall()
    conn.close()
    return detalles