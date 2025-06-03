from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

MYSQL_USER = "root"         # Tu nombre de usuario de MySQL
MYSQL_PASSWORD = "1234" # Tu contraseña de MySQL
MYSQL_HOST = "localhost"               # La dirección de tu servidor MySQL (o su IP)
MYSQL_PORT = "3306"                    # El puerto de tu servidor MySQL (el default es 3306)
MYSQL_DB = "gimnasio"                  # El nombre de la base de datos que creaste en Workbench


DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Crear el engine. Es el punto de entrada para interactuar con la base de datos.
# pool_recycle=3600 es una buena práctica para conexiones a MySQL para evitar problemas de timeout.
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600
)


Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
 
    db = SessionLocal()
    try:
        yield db  # 'yield' permite que esta función sea usada como un context manager (ver ejemplo arriba)
    finally:
        db.close() # Cierra la sesión para liberar recursos

def create_all_tables():
    print("Intentando conectar y verificar/crear tablas en MySQL...")
    try:
        
        Base.metadata.create_all(bind=engine)
        print("Verificación/Creación de tablas completada.")
    except Exception as e:
        print(f"Error al intentar conectar o crear tablas: {e}")
        print("Por favor, verifica:")
        print("- Que el servidor MySQL esté corriendo.")
        print("- Que la base de datos 'gimnasio' exista.")
        print("- Que el usuario y contraseña en database.py sean correctos.")
        print("- Que el host y puerto sean correctos.")

