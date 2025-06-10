# Esto le dice a Render que ejecute Gunicorn para tu aplicación Flask.
# El `$PORT` es una variable de entorno que Render inyecta automáticamente.
# 'app:app' significa que el objeto Flask se llama 'app' y está en el archivo 'app.py'.
web: gunicorn --bind 0.0.0.0:$PORT app:app
