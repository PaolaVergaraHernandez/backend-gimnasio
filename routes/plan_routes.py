# routes/plan_routes.py

from flask import Blueprint, jsonify, request # Importa Blueprint, jsonify, request

# Importa las funciones handler especificas para planes
from handlers.plan_handlers import (
    # Nombre de la funcion handler corregido para coincidir con el handler
    obtener_todos_planes_sp,
    obtener_plan_por_id_sp,
    agregar_plan_sp,
    actualizar_plan_sp,
    eliminar_plan_sp
)

# --- IMPORTANTE: Importa el decorador token_required ---
from .auth_middleware import token_required

# Crea un Blueprint para las rutas de planes
# url_prefix es '/api/planes'
planes_bp = Blueprint('planes', __name__, url_prefix='/api/planes')

# --- Rutas (Endpoints) definidas con el Blueprint de planes ---
# --- AHORA PROTEGIDAS CON @token_required ---

@planes_bp.route("/", methods=["GET"]) # Se convierte en '/api/planes/'
@token_required # <--- APLICA EL DECORADOR AQUÍ
def get_todos_planes(): # Nombre de la funcion de ruta corregido
    """Endpoint para obtener todos los planes."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó todos los planes.")
    resultado = obtener_todos_planes_sp() # Llama al handler con el nombre corregido
    if "error" in resultado:
        return jsonify(resultado), 500
    return jsonify(resultado), 200

@planes_bp.route("/<int:id_plan>", methods=["GET"]) # Se convierte en '/api/planes/<int:id_plan>'
@token_required # <--- APLICA EL DECORADOR AQUÍ
def get_plan_por_id(id_plan):
    """Endpoint para obtener un plan por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) solicitó plan ID: {id_plan}.")
    resultado = obtener_plan_por_id_sp(id_plan)

    if "error" in resultado:
        # Si el handler devuelve un error (ej: ID invalido por validacion SIGNAL)
        # El handler ya devuelve {"error": "Mensaje de validacion"}
        return jsonify(resultado), 500 # O podria ser 400 para errores de validacion del cliente

    # El handler ahora devuelve {'message': '... no encontrado'} si el ID es valido pero no existe
    # Verificamos si el resultado contiene la clave 'message' y el texto de "no encontrado"
    if "message" in resultado and f"Plan con ID {id_plan} no encontrado." in resultado["message"]:
        return jsonify(resultado), 404 # Not Found (devuelve el mensaje del handler)

    # Si no hay error y no hay mensaje de 'no encontrado', asumimos que el handler devolvio los datos del plan
    return jsonify(resultado), 200 # OK

@planes_bp.route("/", methods=["POST"]) # Se convierte en '/api/planes/' para POST
@token_required # <--- APLICA EL DECORADOR AQUÍ
def add_plan():
    """Endpoint para agregar un nuevo plan."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó crear un plan.")
    datos_plan = request.get_json() # Obtiene JSON

    if not datos_plan:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400 # Bad Request

    # Llama al handler de agregar
    resultado = agregar_plan_sp(
        nombre=datos_plan.get("nombre"),
        descripcion=datos_plan.get("descripcion"),
        precio=datos_plan.get("precio"), # Espera numero o string convertible a Decimal
        duracion_dias=datos_plan.get("duracion_dias")
    )

    if "error" in resultado:
        return jsonify(resultado), 400 # Errores de validacion/logica de BD
    return jsonify(resultado), 201 # Created

@planes_bp.route("/<int:id_plan>", methods=["PUT"]) # Se convierte en '/api/planes/<int:id_plan>' para PUT
@token_required # <--- APLICA EL DECORADOR AQUÍ
def update_plan(id_plan):
    """Endpoint para actualizar un plan existente."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó actualizar plan ID: {id_plan}.")
    datos_plan = request.get_json() # Obtiene JSON

    if not datos_plan:
        return jsonify({"error": "Se esperan datos en formato JSON"}), 400 # Bad Request

    # Llama al handler de actualizar
    resultado = actualizar_plan_sp(
        id_plan=id_plan,
        nombre=datos_plan.get("nombre"),
        descripcion=datos_plan.get("descripcion"),
        precio=datos_plan.get("precio"),
        duracion_dias=datos_plan.get("duracion_dias")
    )

    if "error" in resultado:
        return jsonify(resultado), 400 # Errores de validacion/logica de BD
    return jsonify(resultado), 200 # OK

@planes_bp.route("/<int:id_plan>", methods=["DELETE"]) # Se convierte en '/api/planes/<int:id_plan>' para DELETE
@token_required # <--- APLICA EL DECORADOR AQUÍ
def delete_plan(id_plan):
    """Endpoint para eliminar un plan por su ID."""
    # Opcional: print(f"Usuario {request.user_email} (UID: {request.user_id}) intentó eliminar plan ID: {id_plan}.")
    # Llama al handler de eliminar
    resultado = eliminar_plan_sp(id_plan)

    if "error" in resultado:
        return jsonify(resultado), 500 # Error interno (ej: FK)
    return jsonify(resultado), 200 # OK