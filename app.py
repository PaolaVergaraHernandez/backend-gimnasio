# app.py

import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from firebase_admin import credentials, auth, initialize_app # <-- Importaciones de Firebase
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


# Importar de database.py
from database import get_db, create_all_tables, Product

# --- Configuración de Flask ---
app = Flask(__name__)
# CORS: Permite solicitudes desde el frontend de desarrollo (localhost:4200)
# y desde tu frontend desplegado en Firebase Hosting (si llegas a usarlo).
# Para depuración, CORS(app) es muy permisivo por defecto. Para producción, usa origins específicos.
CORS(app, resources={r"/*": {"origins": ["http://localhost:4200", "https://gimnasio-bd67b.web.app"]}})

# --- Inicialización de Firebase Admin SDK ---
try:
    # Asegúrate de que 'firebase_credentials.json' esté en la misma carpeta que app.py
    # Si no tienes este archivo, descárgalo de Firebase Console > Project settings > Service accounts
    # Y guárdalo como firebase_credentials.json en la carpeta de tu backend.
    cred = credentials.Certificate('firebase_credentials.json')
    initialize_app(cred)
    print("Firebase Admin SDK inicializado exitosamente.")
except Exception as e:
    print(f"Error al inicializar Firebase Admin SDK: {e}")
    print("Asegúrate de tener el archivo 'firebase_credentials.json' correcto.")
    # Si Firebase Admin SDK no se inicializa, las funciones de autenticación fallarán.
    # Considera si la aplicación debe continuar sin esto.


# --- Middleware para manejar la sesión de DB por cada solicitud ---
@app.before_request
def before_request():
    # Abre una nueva sesión de DB para cada solicitud y la guarda en `g`
    g.db = next(get_db())

@app.after_request
def after_request(response):
    # Cierra la sesión de DB después de cada solicitud
    if hasattr(g, 'db'):
        g.db.close()
    return response


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

# Ruta de Login
@app.route("/login", methods=["POST", "OPTIONS"])
def login():
    print(f"DEBUG: Solicitud recibida en /login. Método: {request.method}")
    print(f"DEBUG: Headers de la solicitud: {request.headers}")

    if request.method == 'OPTIONS':
        print("DEBUG: Manejando solicitud OPTIONS (preflight CORS).")
        response = jsonify({"message": "CORS preflight OK"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST")
        return response

    if request.method == 'POST':
        print("DEBUG: Manejando solicitud POST.")
        try:
            data = request.get_json()
            if data is None:
                print("DEBUG: Request body is not JSON or is empty.")
                return jsonify({"error": "Contenido de la solicitud no es JSON válido o está vacío"}), 400

            # Es crucial que el frontend envíe el idToken que obtiene de Firebase Authentication
            id_token = data.get('idToken') # <-- Se espera un campo 'idToken'
            print(f"DEBUG: idToken recibido: {id_token[:30]}..." if id_token else "DEBUG: No se recibió idToken.")

            if not id_token:
                print("DEBUG: idToken no proporcionado en la solicitud.")
                return jsonify({"error": "idToken es requerido"}), 400

            # Verificar el token de Firebase usando Firebase Admin SDK
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email', 'No disponible')

            print(f"DEBUG: Token de Firebase verificado con éxito para UID: {uid}, Email: {email}.")
            return jsonify({
                "message": "Autenticación exitosa",
                "uid": uid,
                "email": email
            }), 200

        except ValueError as ve:
            print(f"ERROR: Error de formato JSON: {ve}")
            return jsonify({"error": f"Formato de datos inválido: {ve}"}), 400
        except Exception as e:
            print(f"ERROR: Error en la verificación del token de Firebase: {e}")
            return jsonify({"error": f"Error de autenticación: {e}"}), 401
    else:
        print(f"DEBUG: Método {request.method} no permitido explícitamente en /login.")
        return jsonify({"error": "Método no permitido"}), 405


# --- Rutas CRUD de Productos (¡Ahora usando SQLAlchemy!) ---

# Ruta para obtener todos los productos
@app.route("/productos", methods=["GET"])
#@token_required # <-- Descomentar para proteger la ruta en producción
def get_productos():
    try:
        db: Session = g.db
        productos = db.query(Product).all()
        return jsonify([p.to_dict() for p in productos]), 200
    except SQLAlchemyError as e:
        print(f"ERROR: Error de SQLAlchemy al obtener productos: {e}")
        return jsonify({"error": "Error interno del servidor al cargar productos desde la DB"}), 500
    except Exception as e:
        print(f"ERROR: Error inesperado al obtener productos: {e}")
        return jsonify({"error": "Error inesperado al cargar productos"}), 500

# Ruta para añadir un nuevo producto
@app.route("/productos", methods=["POST"])
#@token_required # <-- Descomentar para proteger la ruta en producción
def add_producto():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos de producto son requeridos"}), 400

    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    precio = data.get('precio')
    stock = data.get('stock')
    imagen_url = data.get('imagen_url')

    if not all([nombre, precio is not None, stock is not None]):
        return jsonify({"error": "Faltan datos obligatorios: nombre, precio, stock"}), 400

    try:
        db: Session = g.db
        new_product = Product(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen_url=imagen_url
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return jsonify({
            "message": "Producto añadido con éxito",
            "producto": new_product.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR: Error de SQLAlchemy al añadir producto: {e}")
        return jsonify({"error": "Error interno del servidor al añadir producto"}), 500
    except Exception as e:
        print(f"ERROR: Error inesperado al añadir producto: {e}")
        return jsonify({"error": "Error inesperado al añadir producto"}), 500

# Ruta para actualizar un producto existente
@app.route("/productos/<int:product_id>", methods=["PUT"])
#@token_required # <-- Descomentar para proteger la ruta en producción
def update_producto(product_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos de actualización son requeridos"}), 400

    try:
        db: Session = g.db
        product_to_update = db.query(Product).filter_by(id_producto=product_id).first()

        if not product_to_update:
            return jsonify({"error": "Producto no encontrado"}), 404

        for key, value in data.items():
            if hasattr(product_to_update, key):
                setattr(product_to_update, key, value)

        db.commit()
        db.refresh(product_to_update)

        return jsonify({"message": "Producto actualizado con éxito", "producto": product_to_update.to_dict()}), 200
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR: Error de SQLAlchemy al actualizar producto: {e}")
        return jsonify({"error": "Error interno del servidor al actualizar producto"}), 500
    except Exception as e:
        print(f"ERROR: Error inesperado al actualizar producto: {e}")
        return jsonify({"error": "Error inesperado al actualizar producto"}), 500

# Ruta para eliminar un producto
@app.route("/productos/<int:product_id>", methods=["DELETE"])
#@token_required # <-- Descomentar para proteger la ruta en producción
def delete_producto(product_id):
    try:
        db: Session = g.db
        product_to_delete = db.query(Product).filter_by(id_producto=product_id).first()

        if not product_to_delete:
            return jsonify({"error": "Producto no encontrado"}), 404

        db.delete(product_to_delete)
        db.commit()

        return jsonify({"message": "Producto eliminado con éxito"}), 200
    except SQLAlchemyError as e:
        db.rollback()
        print(f"ERROR: Error de SQLAlchemy al eliminar producto: {e}")
        return jsonify({"error": "Error interno del servidor al eliminar producto"}), 500
    except Exception as e:
        print(f"ERROR: Error inesperado al eliminar producto: {e}")
        return jsonify({"error": "Error inesperado al eliminar producto"}), 500

# Ruta para obtener un producto por ID
@app.route("/productos/<int:product_id>", methods=["GET"])
#@token_required # <-- Descomentar para proteger la ruta en producción
def get_producto_by_id(product_id):
    try:
        db: Session = g.db
        producto = db.query(Product).filter_by(id_producto=product_id).first()
        if producto:
            return jsonify(producto.to_dict()), 200
        return jsonify({"error": "Producto no encontrado"}), 404
    except SQLAlchemyError as e:
        print(f"ERROR: Error de SQLAlchemy al obtener producto por ID: {e}")
        return jsonify({"error": "Error interno del servidor al obtener producto por ID"}), 500
    except Exception as e:
        print(f"ERROR: Error inesperado al obtener producto por ID: {e}")
        return jsonify({"error": "Error inesperado al obtener producto por ID"}), 500


# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    # Llama a esta función para asegurar que las tablas de SQLAlchemy existan
    # (basado en el modelo Product).
    # Esta función intentará crear la tabla 'productos' si no existe.
    create_all_tables()
    # Asegúrate de que el puerto 5000 esté libre o cámbialo.
    # debug=True es bueno para desarrollo, pero desactívalo en producción.
    app.run(debug=True, port=5000)

