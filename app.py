import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, auth, initialize_app
from functools import wraps
from flask_mysqldb import MySQL
import pymysql.err # Importa los errores específicos de PyMySQL para un mejor manejo

# --- Configuración de Flask ---
app = Flask(__name__)
CORS(app)

# --- Configuración de la Conexión a MySQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234' # ¡CAMBIA ESTO!
app.config['MYSQL_DB'] = 'gimnasio'  # ¡CAMBIA ESTO!
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # Para obtener resultados como diccionarios

mysql = MySQL(app) # Inicializa la extensión MySQL

# --- Inicialización de Firebase Admin SDK ---
try:
    # Asegúrate de que 'firebase_credentials.json' esté en la misma carpeta que app.py
    cred = credentials.Certificate('firebase_credentials.json')
    initialize_app(cred)
    print("Firebase Admin SDK inicializado exitosamente.")
except Exception as e:
    print(f"Error al inicializar Firebase Admin SDK: {e}")
    # Considera salir de la aplicación si Firebase Admin SDK no se inicializa correctamente.
    # import sys
    # sys.exit(1)


# --- Decorador para proteger rutas con token de Firebase ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' not in request.headers:
            return jsonify({'message': 'Token de autorización es requerido'}), 401

        token = request.headers['Authorization'].split(' ')[1]
        try:
            decoded_token = auth.verify_id_token(token)
            request.user_id = decoded_token['uid']
            request.user_email = decoded_token.get('email')
        except Exception as e:
            return jsonify({'message': f'Token inválido o expirado: {e}'}), 401
        return f(*args, **kwargs)
    return decorated


# --- Rutas (Endpoints) ---

# Ruta de Login (ya establecida)
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == 'OPTIONS':
        response = jsonify({"message": "CORS preflight OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    data = request.get_json()
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({"error": "idToken es requerido"}), 400

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', 'No disponible')

        return jsonify({
            "message": "Autenticación exitosa",
            "uid": uid,
            "email": email
        }), 200

    except Exception as e:
        print(f"Error en la verificación del token de Firebase: {e}")
        return jsonify({"error": f"Error de autenticación: {e}"}), 401


# --- Rutas CRUD de Productos (Usando Procedimientos Almacenados) ---

# Ruta para obtener todos los productos (protegida)
@app.route("/productos", methods=["GET"])
#@token_required
def get_productos():
    try:
        cur = mysql.connection.cursor()
        cur.callproc('sp_ObtenerTodosProductos') # Llama al procedimiento almacenado
        productos = cur.fetchall()
        cur.close()
        return jsonify(productos), 200
    except pymysql.err.OperationalError as e:
        print(f"Error de MySQL al obtener productos: {e}")
        if e.args[0] == 1644: # Código de error para SIGNAL SQLSTATE '45000'
            return jsonify({"error": e.args[1]}), 400
        return jsonify({"error": "Error interno del servidor al cargar productos"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener productos: {e}")
        return jsonify({"error": "Error inesperado al cargar productos"}), 500

# Ruta para añadir un nuevo producto (protegida)
@app.route("/productos", methods=["POST"])
@token_required
def add_producto():
    data = request.get_json()

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    precio = data.get('precio')
    stock = data.get('stock')
    imagen_url = data.get('imagen_url')

    if not all([nombre, precio is not None, stock is not None]):
        return jsonify({"error": "Faltan datos obligatorios: nombre, precio, stock"}), 400

    try:
        cur = mysql.connection.cursor()
        # Llama al procedimiento almacenado con los parámetros
        cur.callproc('sp_AgregarProducto', (nombre, descripcion, precio, stock, imagen_url))
        mysql.connection.commit()

        # Tu SP no devuelve el ID, así que lo obtenemos con LAST_INSERT_ID()
        cur.execute("SELECT LAST_INSERT_ID() as id_producto;")
        new_id = cur.fetchone()['id_producto']
        cur.close()

        return jsonify({
            "message": "Producto añadido con éxito",
            "producto": {"id_producto": new_id, "nombre": nombre, "descripcion": descripcion, "precio": precio, "stock": stock, "imagen_url": imagen_url}
        }), 201
    except pymysql.err.OperationalError as e:
        print(f"Error de MySQL al añadir producto: {e}")
        if e.args[0] == 1644:
            return jsonify({"error": e.args[1]}), 400
        return jsonify({"error": "Error interno del servidor al añadir producto"}), 500
    except Exception as e:
        print(f"Error inesperado al añadir producto: {e}")
        return jsonify({"error": "Error inesperado al añadir producto"}), 500

# Ruta para actualizar un producto existente (protegida)
@app.route("/productos/<int:product_id>", methods=["PUT"])
@token_required
def update_producto(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Datos de actualización son requeridos"}), 400

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    precio = data.get('precio')
    stock = data.get('stock')
    imagen_url = data.get('imagen_url')

    if not all([nombre, precio is not None, stock is not None]):
        return jsonify({"error": "Faltan datos obligatorios para actualizar: nombre, precio, stock"}), 400

    try:
        cur = mysql.connection.cursor()
        # Llama al procedimiento almacenado con todos los parámetros
        cur.callproc('sp_ActualizarProducto', (product_id, nombre, descripcion, precio, stock, imagen_url))
        mysql.connection.commit()

        # Opcional: Obtener el producto actualizado para devolverlo
        cur.callproc('sp_ObtenerProductoPorID', (product_id,))
        updated_product = cur.fetchone()
        cur.close()

        if updated_product:
            print(f"Producto {product_id} actualizado.")
            return jsonify({"message": "Producto actualizado con éxito", "producto": updated_product}), 200
        else:
            return jsonify({"error": "Producto no encontrado después de actualizar"}), 404
    except pymysql.err.OperationalError as e:
        print(f"Error de MySQL al actualizar producto: {e}")
        if e.args[0] == 1644:
            return jsonify({"error": e.args[1]}), 400
        return jsonify({"error": "Error interno del servidor al actualizar producto"}), 500
    except Exception as e:
        print(f"Error inesperado al actualizar producto: {e}")
        return jsonify({"error": "Error inesperado al actualizar producto"}), 500

# Ruta para eliminar un producto (protegida)
@app.route("/productos/<int:product_id>", methods=["DELETE"])
@token_required
def delete_producto(product_id):
    try:
        cur = mysql.connection.cursor()
        cur.callproc('sp_EliminarProducto', (product_id,))
        mysql.connection.commit()
        cur.close()

        print(f"Producto {product_id} eliminado.")
        return jsonify({"message": "Producto eliminado con éxito"}), 200
    except pymysql.err.OperationalError as e:
        print(f"Error de MySQL al eliminar producto: {e}")
        if e.args[0] == 1644:
            return jsonify({"error": e.args[1]}), 400
        return jsonify({"error": "Error interno del servidor al eliminar producto"}), 500
    except Exception as e:
        print(f"Error inesperado al eliminar producto: {e}")
        return jsonify({"error": "Error inesperado al eliminar producto"}), 500


# --- Ruta para obtener un producto por ID (protegida, adicional) ---
@app.route("/productos/<int:product_id>", methods=["GET"])
#@token_required
def get_producto_by_id(product_id):
    try:
        cur = mysql.connection.cursor()
        cur.callproc('sp_ObtenerProductoPorID', (product_id,))
        producto = cur.fetchone()
        cur.close()
        if producto:
            return jsonify(producto), 200
        return jsonify({"error": "Producto no encontrado"}), 404
    except pymysql.err.OperationalError as e:
        print(f"Error de MySQL al obtener producto por ID: {e}")
        if e.args[0] == 1644:
            return jsonify({"error": e.args[1]}), 400
        return jsonify({"error": "Error interno del servidor al obtener producto por ID"}), 500
    except Exception as e:
        print(f"Error inesperado al obtener producto por ID: {e}")
        return jsonify({"error": "Error inesperado al obtener producto por ID"}), 500


# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    app.run(debug=True)