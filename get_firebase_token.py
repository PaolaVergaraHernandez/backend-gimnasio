import requests
import json

# --- PASO 1: REEMPLAZA ESTO CON TU CLAVE DE API WEB DE FIREBASE ---
# Puedes encontrarla en la Consola de Firebase:
# 1. Ve a tu proyecto de Firebase.
# 2. Haz clic en el icono de "Engranaje" (Project settings) en la barra lateral izquierda.
# 3. En la pestaña "General", busca "Web API Key". Copia esa clave.
FIREBASE_WEB_API_KEY = "AIzaSyADKFJpW9Ge0oLitSOU1DtY_6FUzMDuKLQ"


# --- PASO 2: TUS CREDENCIALES DE ADMINISTRADOR ---
# Usando el email y la contraseña de tu usuario administrador en Firebase
EMAIL = "administrador@gmail.com" # <--- ¡AHORA CON TU CORREO!
PASSWORD = "CAFECONLECHE" # <--- ¡AHORA CON TU CONTRASEÑA!

def get_id_token(email, password, api_key):
    """
    Inicia sesion en Firebase Authentication REST API y retorna el ID Token.
    """
    rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })

    try:
        response = requests.post(rest_api_url, headers=headers, data=payload)
        response.raise_for_status() # Lanza un error si el codigo de estado HTTP es 4xx o 5xx
        data = response.json()
        return data.get("idToken")
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener ID Token de Firebase: {e}")
        if hasattr(response, 'text'):
            print(f"Respuesta de Firebase (error): {response.text}")
        return None

if __name__ == "__main__":
    print("Intentando obtener ID Token de Firebase...")
    id_token = get_id_token(EMAIL, PASSWORD, FIREBASE_WEB_API_KEY)
    if id_token:
        print("\n--- ID Token Obtenido Exitosamente ---")
        print(id_token)
        print("\n¡Copia este token! Lo usaras en Postman para probar el endpoint /api/auth/login.")
    else:
        print("No se pudo obtener el ID Token. Revisa tu EMAIL, PASSWORD y FIREBASE_WEB_API_KEY.")

