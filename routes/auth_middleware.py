# src/app/routes/auth_middleware.py

from flask import request, jsonify
from functools import wraps
from firebase_admin import auth # Asegúrate de que 'auth' está importado aquí

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Firebase token se envía en el encabezado Authorization como 'Bearer <token>'
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token de autenticación es requerido!'}), 401 # Unauthorized

        try:
            # Verificar el token de Firebase
            # Esto decodifica el token y verifica su firma, expiración, etc.
            decoded_token = auth.verify_id_token(token)
            # El UID del usuario autenticado se almacena en el request context
            # para que las funciones de ruta puedan acceder a él.
            request.user_id = decoded_token['uid']
            request.user_email = decoded_token.get('email') # Opcional, si necesitas el email

        except Exception as e:
            # Manejo de varios errores que Firebase puede lanzar (token expirado, inválido, etc.)
            print(f"Error al verificar el token de Firebase: {e}")
            return jsonify({'message': 'Token inválido o expirado!', 'error': str(e)}), 401 # Unauthorized

        return f(*args, **kwargs)
    return decorated