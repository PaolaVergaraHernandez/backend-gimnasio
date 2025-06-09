# database.py

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError, SQLAlchemyError

# --- Configuración de Conexión a MySQL ---
# ¡IMPORTANTE! Cambia la contraseña '1234' por una más segura para producción.
# Para entorno de desarrollo, asegúrate de que MySQL esté corriendo
# y que las credenciales sean correctas.
MYSQL_USER = "u7a32dpxdefscix0"
MYSQL_PASSWORD = "Gk0Mwirj7wHkaxOUjl41"
MYSQL_HOST = "bpngdi36dwtobigkpb9r-mysql.services.clever-cloud.com"
MYSQL_PORT = "3306"
MYSQL_DB = "bpngdi36dwtobigkpb9r"

# URL de la base de datos para SQLAlchemy
# Usamos mysql+mysqlconnector porque es la implementación recomendada para MySQL con SQLAlchemy
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

# Crear el engine. Es el punto de entrada para interactuar con la base de datos.
# pool_recycle=3600 es una buena práctica para conexiones a MySQL para evitar problemas de timeout.
# echo=True mostrará las queries SQL generadas por SQLAlchemy en la consola (útil para depuración)
engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,
    echo=True
)

# Base declarativa para tus modelos de SQLAlchemy
Base = declarative_base()

# --- Definición del Modelo de Producto ---
# Este modelo se mapeará a una tabla llamada 'productos' en tu base de datos MySQL.
# Asegúrate de que los nombres de las columnas coincidan con los de tu tabla existente.
class Product(Base):
    __tablename__ = 'productos' # Nombre de tu tabla en la base de datos

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(String(255), nullable=True)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    imagen_url = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Product(id={self.id_producto}, nombre='{self.nombre}')>"

    # Método para convertir el objeto Product en un diccionario (útil para jsonify)
    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "stock": self.stock,
            "imagen_url": self.imagen_url
        }

# Configuración de la sesión local para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener una sesión de base de datos (se usa con Flask's `g` o `inject`)
def get_db():
    db = SessionLocal()
    try:
        yield db # 'yield' permite que esta función sea usada como un context manager
    finally:
        db.close() # Cierra la sesión para liberar recursos

# Función para crear todas las tablas definidas en los modelos (si no existen)
def create_all_tables():
    print("\n--- Iniciando conexión y verificación/creación de tablas en MySQL ---")
    try:
        # Intenta conectar y crear las tablas (si no existen)
        Base.metadata.create_all(bind=engine)
        print("--- Verificación/Creación de tablas completada exitosamente. ---")
    except OperationalError as e:
        print(f"\n!!! ERROR CRÍTICO DE CONEXIÓN A MySQL: {e} !!!")
        print("Por favor, verifica:")
        print("- Que el servidor MySQL (XAMPP/WAMP/etc.) esté corriendo.")
        print(f"- Que la base de datos '{MYSQL_DB}' exista.")
        print(f"- Que el usuario '{MYSQL_USER}' y la contraseña sean correctos en database.py.")
        print(f"- Que el host '{MYSQL_HOST}' y el puerto '{MYSQL_PORT}' sean correctos.")
        print("No se pudo establecer la conexión a la base de datos. Las operaciones CRUD fallarán.")
    except SQLAlchemyError as e:
        print(f"\n!!! ERROR DE SQLAlchemy al crear tablas: {e} !!!")
        print("Asegúrate de que la configuración de la base de datos sea correcta y que no haya problemas de permisos.")
    except Exception as e:
        print(f"\n!!! ERROR INESPERADO al intentar conectar o crear tablas: {e} !!!")

