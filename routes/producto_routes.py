
from flask import Blueprint, jsonify, request, g
from decimal import Decimal

from handlers.producto_handlers import (
    obtener_todos_productos_sp,
    obtener_producto_por_id_sp,
    agregar_producto_sp,
    actualizar_producto_sp,
    eliminar_producto_sp
)

from .auth_middleware import token_required

productos_bp = Blueprint('productos', __name__, url_prefix='/api/productos')
#rutas publlicas 

@productos_bp.route("/", methods=["GET"])
#@token_required # <--- Aplica el decorador aquí para PROTEGER esta ruta
def get_todos_productos():
    """Endpoint para obtener todos los productos."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó todos los productos.")
    resultado = obtener_todos_productos_sp()
    if "error" in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado), 200

@productos_bp.route("/<int:id_producto>", methods=["GET"])
#@token_required # <--- Aplica el decorador aquí para PROTEGER esta ruta
def get_producto_por_id(id_producto):
    """Endpoint para obtener un producto por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó producto ID: {id_producto}.")
    resultado = obtener_producto_por_id_sp(id_producto)

    if "error" in resultado:
        return jsonify(resultado), 500

    if "message" in resultado and f"Producto con ID {id_producto} no encontrado." in resultado["message"]:
        return jsonify(resultado), 404

    return jsonify(resultado), 200

@productos_bp.route("/", methods=["POST"])
@token_required # <--- Aplica el decorador aquí para PROTEGER esta ruta
def add_producto():
    """Endpoint para agregar un nuevo producto."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó crear un producto.")
    datos_producto = request.get_json()

    if not datos_producto:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400

    nombre = datos_producto.get("nombre")
    descripcion = datos_producto.get("descripcion")
    precio_str = datos_producto.get("precio")
    stock = datos_producto.get("stock")
    imagen_url = datos_producto.get("imagen_url")

    if not all([nombre, precio_str is not None, stock is not None]):
        return jsonify({"error": "Faltan campos obligatorios (nombre, precio, stock)."}), 400

    try:
        precio = Decimal(str(precio_str))
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido."}), 400

    resultado = agregar_producto_sp(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        imagen_url=imagen_url
    )

    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 201

@productos_bp.route("/<int:id_producto>", methods=["PUT"])
@token_required # <--- Aplica el decorador aquí para PROTEGER esta ruta
def update_producto(id_producto):
    """Endpoint para actualizar un producto existente."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó actualizar producto ID: {id_producto}.")
    datos_producto = request.get_json()

    if not datos_producto:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400

    nombre = datos_producto.get("nombre")
    descripcion = datos_producto.get("descripcion")
    precio_str = datos_producto.get("precio")
    stock = datos_producto.get("stock")
    imagen_url = datos_producto.get("imagen_url")

    if not all([nombre, precio_str is not None, stock is not None]):
        return jsonify({"error": "Faltan campos obligatorios (nombre, precio, stock)."}), 400

    try:
        precio = Decimal(str(precio_str))
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido."}), 400

    resultado = actualizar_producto_sp(
        id_producto=id_producto,
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        imagen_url=imagen_url
    )

    if "error" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 200

@productos_bp.route("/<int:id_producto>", methods=["DELETE"])
@token_required # <--- Aplica el decorador aquí para PROTEGER esta ruta
def delete_producto(id_producto):
    """Endpoint para eliminar un producto por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó eliminar producto ID: {id_producto}.")
    resultado = eliminar_producto_sp(id_producto)

    if "error" in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado), 200