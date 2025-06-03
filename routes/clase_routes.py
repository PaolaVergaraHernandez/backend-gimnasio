# src/app/routes/clase_routes.py

from flask import Blueprint, jsonify, request # Importa Blueprint, jsonify, request

# Importa las funciones handler especificas para clases
from handlers.clase_handlers import (
    obtener_todas_clases_sp,
    obtener_clase_por_id_sp,
    agregar_clase_sp,
    actualizar_clase_sp,
    eliminar_clase_sp
)

# --- IMPORTANTE: Importa el decorador token_required ---
from .auth_middleware import token_required

clases_bp = Blueprint('clases', __name__, url_prefix='/api/clases')

# --- Rutas (Endpoints) definidas con el Blueprint ---
# --- AHORA PROTEGIDAS CON @token_required ---

@clases_bp.route("/", methods=["GET"]) # La ruta '/' aqui se convierte en '/api/clases/' por el url_prefix
@token_required # <--- APLICA EL DECORADOR AQUÍ
def get_todas_clases():
    """Endpoint para obtener todas las clases."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó todas las clases.")
    resultado = obtener_todas_clases_sp() # Llama al handler de obtener todas
    if "error" in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado), 200
#pp
@clases_bp.route("/<int:id_clase>", methods=["GET"])
@token_required # <--- APLICA EL DECORADOR AQUÍ
def get_clase_por_id(id_clase):
    """Endpoint para obtener una clase por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó clase ID: {id_clase}.")
    resultado = obtener_clase_por_id_sp(id_clase)
    if "error" in resultado:
        return jsonify(resultado), 500
    if "message" in resultado and f"Clase con ID {id_clase} no encontrada." in resultado["message"]:
        return jsonify(resultado), 404
    return jsonify(resultado), 200
#pp

@clases_bp.route("/", methods=["POST"]) # La ruta '/' aqui se convierte en '/api/clases/' para POST
@token_required # <--- APLICA EL DECORADOR AQUÍ
def add_clase():
    """Endpoint para agregar una nueva clase."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó crear una clase.")
    datos_clase = request.get_json() # Obtiene JSON del cuerpo

    if not datos_clase:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400 # Bad Request

    # Llama al handler de agregar, pasando los datos del JSON
    resultado = agregar_clase_sp(
        nombre=datos_clase.get("nombre"),
        descripcion=datos_clase.get("descripcion"),
        instructor=datos_clase.get("instructor"),
        horario=datos_clase.get("horario"), # Espera formato string 'HH:MM:SS'
        duracion=datos_clase.get("duracion"),
        cupo_maximo=datos_clase.get("cupo_maximo")
    )

    if "error" in resultado:
        return jsonify(resultado), 400 # Errores de validacion/logica de BD (ej: SIGNAL)
    return jsonify(resultado), 201 # Created

@clases_bp.route("/<int:id_clase>", methods=["PUT"]) # '/<int:id_clase>' se convierte en '/api/clases/<int:id_clase>' para PUT
@token_required # <--- APLICA EL DECORADOR AQUÍ
def update_clase(id_clase):
    """Endpoint para actualizar una clase existente."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó actualizar clase ID: {id_clase}.")
    datos_clase = request.get_json() # Obtiene JSON del cuerpo

    if not datos_clase:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400 # Bad Request

    # Llama al handler de actualizar, pasando ID de URL y datos del JSON
    resultado = actualizar_clase_sp(
        id_clase=id_clase,
        nombre=datos_clase.get("nombre"),
        descripcion=datos_clase.get("descripcion"),
        instructor=datos_clase.get("instructor"),
        horario=datos_clase.get("horario"), # Espera formato string 'HH:MM:SS'
        duracion=datos_clase.get("duracion"),
        cupo_maximo=datos_clase.get("cupo_maximo")
    )

    if "error" in resultado:
        return jsonify(resultado), 400 # Errores de validacion/logica de BD
    return jsonify(resultado), 200 # OK

@clases_bp.route("/<int:id_clase>", methods=["DELETE"]) # '/<int:id_clase>' se convierte en '/api/clases/<int:id_clase>' para DELETE
@token_required # <--- APLICA EL DECORADOR AQUÍ
def delete_clase(id_clase):
    """Endpoint para eliminar una clase por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó eliminar clase ID: {id_clase}.")
    # Llama al handler de eliminar, pasando ID de URL
    resultado = eliminar_clase_sp(id_clase)

    if "error" in resultado:
        return jsonify(resultado), 500 # Error interno (ej: FK constraint)
    return jsonify(resultado), 200 # OK