
from database import engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# --- Handler para sp_ObtenerTodasClases ---
def obtener_todas_clases_sp():
    """
    Llama al procedimiento almacenado sp_ObtenerTodasClases y devuelve los resultados.
    """
    conn = None # Inicializa la conexion a None
    try:
        conn = engine.connect() # Establece la conexion
        # Define la llamada al procedimiento almacenado
        sql_call = text("CALL sp_ObtenerTodasClases()")

        # Ejecuta la llamada al procedimiento
        with conn.execute(sql_call) as resultado:
            # Obtiene los nombres de las columnas del resultado
            column_keys = resultado.keys()
            # Obtiene todas las filas del resultado
            filas = resultado.fetchall()

        # Convierte cada fila a un diccionario usando los nombres de las columnas
        lista_clases_dict = []
        for fila in filas:
            clase_dict = dict(zip(column_keys, fila))
            # No necesitamos conversiones especiales para horario (VARCHAR) u otros tipos basicos serializables por JSON
            lista_clases_dict.append(clase_dict)

        # Si todo sale bien, devuelve la lista de diccionarios
        return lista_clases_dict

    except SQLAlchemyError as e:
        # Captura errores especificos de SQLAlchemy (errores de DB)
        print(f"Error de DB al ejecutar sp_ObtenerTodasClases: {e}")
        # Intenta obtener el mensaje de error original de la base de datos si esta disponible
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        return {"error": f"Error al obtener todas las clases: {error_mensaje_bd}"}
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error inesperado al ejecutar sp_ObtenerTodasClases: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener todas las clases: {e}"}
    finally:
        # Asegura que la conexion se cierre, si se llego a abrir
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_todas_clases_sp): {e_close}")


# --- Handler para sp_ObtenerClasePorID ---
def obtener_clase_por_id_sp(id_clase: int):
    """
    Llama al procedimiento almacenado sp_ObtenerClasePorID y devuelve el resultado.
    """
    conn = None
    try:
        conn = engine.connect()
        # Define la llamada al procedimiento con un parametro de entrada
        sql_call = text("CALL sp_ObtenerClasePorID(:p_id_clase)")

        # Ejecuta la llamada, pasando el parametro como un diccionario
        with conn.execute(sql_call, {"p_id_clase": id_clase}) as resultado:
             # Obtiene los nombres de las columnas
            column_keys = resultado.keys()
            # Obtiene la primera fila (solo esperamos una o ninguna)
            fila = resultado.fetchone()

        # Si se encontro una fila, convertirla a diccionario
        if fila:
            clase_dict = dict(zip(column_keys, fila))
            return clase_dict
        else:
            # Si no se encontro ninguna fila, la clase no existe (o el ID no es valido)
            # Aunque el SP ya valida ID no validos con SIGNAL, si solo no encuentra el ID existente, no hace SIGNAL
            # En este caso, devolvemos un mensaje de no encontrada
            return {"message": f"Clase con ID {id_clase} no encontrada."}


    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ObtenerClasePorID para ID {id_clase}: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)

        # --- Manejo de errores SIGNAL de la DB ---
        # Si el procedimiento usa SIGNAL SQLSTATE '45000' para ID invalido, el mensaje estara aqui.
        if "Se requiere un ID de clase valido." in error_mensaje_bd: # Mensaje del SIGNAL en el SP
             return {"error": "El ID de clase proporcionado no es valido."}

        # Si no es un error SIGNAL conocido, devuelve el error generico de DB
        return {"error": f"Error al obtener clase por ID: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ObtenerClasePorID para ID {id_clase}: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener la clase por ID: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_clase_por_id_sp): {e_close}")


# --- Handler para sp_AgregarClase ---
def agregar_clase_sp(nombre: str, descripcion: str | None, instructor: str, horario: str, duracion: int, cupo_maximo: int):
    """
    Llama al procedimiento almacenado sp_AgregarClase para agregar una nueva clase.
    """
    conn = None
    try:
        conn = engine.connect()
        # Define la llamada al procedimiento con parametros de entrada
        sql_call = text("CALL sp_AgregarClase(:p_nombre, :p_descripcion, :p_instructor, :p_horario, :p_duracion, :p_cupo_maximo)")

        # Define los parametros como un diccionario
        parametros = {
            "p_nombre": nombre,
            "p_descripcion": descripcion, # Puede ser None si el campo en DB permite NULL
            "p_instructor": instructor,
            "p_horario": horario,
            "p_duracion": duracion,
            "p_cupo_maximo": cupo_maximo
        }

        # Ejecuta la llamada. No esperamos un SELECT de este procedimiento.
        #conn.execute(sql_call, parametros) # Execute returns a ResultProxy
        result = conn.execute(sql_call, parametros) # Execute returns a ResultProxy

        # Dado que tu SP no devuelve explicitamente el ID de forma sencilla, solo confirmamos el exito.
        return {"message": "Clase agregada exitosamente."} # , "id_agregada": new_id # Si pudiste obtener el ID

    except IntegrityError as e:
         # Captura errores de integridad (ej: clave primaria duplicada si ID no es autoincremental y lo pasas, etc.)
         print(f"Error de integridad al agregar clase: {e}")
         error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
         return {"error": f"Error de datos al agregar clase: {error_mensaje_bd}"}
    except SQLAlchemyError as e:
        # Captura errores especificos de DB, incluyendo los de SIGNAL SQLSTATE
        print(f"Error de DB al ejecutar sp_AgregarClase: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)

        # --- Manejo de errores SIGNAL de la DB ---
        # Captura mensajes de validacion definidos en el SP con SIGNAL '45000'
        # Los mensajes exactos deben coincidir con los de tus SIGNALs en el SP.
        if "El nombre de la clase no puede estar vacío." in error_mensaje_bd or \
           "El nombre del instructor no puede estar vacío." in error_mensaje_bd or \
           "El horario de la clase no puede estar vacío." in error_mensaje_bd or \
           "La duracion de la clase debe ser un numero positivo." in error_mensaje_bd or \
           "El cupo maximo de la clase debe ser un numero positivo." in error_mensaje_bd:
             return {"error": f"Error de validacion: {error_mensaje_bd}"}


        # Si no es un error SIGNAL conocido, devuelve el error generico de DB
        return {"error": f"Error al agregar clase: {error_mensaje_bd}"}
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error inesperado al ejecutar sp_AgregarClase: {e}")
        return {"error": f"Ocurrio un error inesperado al agregar la clase: {e}"}
    finally:
        # Asegura que la conexion se cierre, si se llego a abrir
        if conn:
            try:
                 # Para operaciones de modificacion (INSERT, UPDATE, DELETE), necesitas hacer commit
                conn.commit() # Confirma los cambios en la base de datos
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (agregar_clase_sp): {e_close}")


# --- Handler para sp_ActualizarClase ---
def actualizar_clase_sp(id_clase: int, nombre: str, descripcion: str | None, instructor: str, horario: str, duracion: int, cupo_maximo: int):
    """
    Llama al procedimiento almacenado sp_ActualizarClase para actualizar una clase existente.
    """
    conn = None
    try:
        conn = engine.connect()
        # Define la llamada al procedimiento con parametros de entrada
        sql_call = text("CALL sp_ActualizarClase(:p_id_clase, :p_nombre, :p_descripcion, :p_instructor, :p_horario, :p_duracion, :p_cupo_maximo)")

        # Define los parametros como un diccionario
        parametros = {
            "p_id_clase": id_clase,
            "p_nombre": nombre,
            "p_descripcion": descripcion, # Puede ser None
            "p_instructor": instructor,
            "p_horario": horario,
            "p_duracion": duracion,
            "p_cupo_maximo": cupo_maximo
        }

        # Ejecuta la llamada. No esperamos un SELECT.
        result = conn.execute(sql_call, parametros) # Execute returns a ResultProxy

        # Puedes verificar result.rowcount despues de ejecutar para saber si se afecto 1 fila
        # result.rowcount sera el numero de filas actualizadas por el UPDATE
        # Si el SP tiene la validacion de ID no existente, result.rowcount sera 0 en ese caso,
        # pero el SP con SIGNAL ya devuelve un error en ese caso, que capturamos abajo.

        # Si la ejecucion llega aqui sin excepcion, se considera exitosa.
        return {"message": f"Clase con ID {id_clase} actualizada exitosamente."}


    except SQLAlchemyError as e:
        # Captura errores especificos de DB, incluyendo los de SIGNAL SQLSTATE
        print(f"Error de DB al ejecutar sp_ActualizarClase para ID {id_clase}: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)

        # --- Manejo de errores SIGNAL de la DB ---
        # Captura mensajes de validacion/existencia definidos en el SP con SIGNAL '45000'
        if "El nombre de la clase no puede estar vacío." in error_mensaje_bd or \
           "El nombre del instructor no puede estar vacío." in error_mensaje_bd or \
           "La duración de la clase debe ser un número positivo." in error_mensaje_bd or \
           "El cupo máximo de la clase debe ser un número positivo." in error_mensaje_bd or \
           "La clase con el ID especificado no existe." in error_mensaje_bd: # Mensaje del SIGNAL para ID no existente
             return {"error": f"Error de validacion/existencia: {error_mensaje_bd}"}

        # Si no es un error SIGNAL conocido, devuelve el error generico de DB
        return {"error": f"Error al actualizar clase: {error_mensaje_bd}"}
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error inesperado al ejecutar sp_ActualizarClase para ID {id_clase}: {e}")
        return {"error": f"Ocurrio un error inesperado al actualizar la clase: {e}"}
    finally:
        if conn:
            try:
                conn.commit() # Confirma los cambios
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (actualizar_clase_sp): {e_close}")


# --- Handler para sp_EliminarClase ---
def eliminar_clase_sp(id_clase: int):
    """
    Llama al procedimiento almacenado sp_EliminarClase para eliminar una clase existente.
    """
    conn = None
    try:
        conn = engine.connect()
        # Define la llamada al procedimiento con un parametro de entrada
        sql_call = text("CALL sp_EliminarClase(:p_id_clase)")

        # Ejecuta la llamada, pasando el parametro
        result = conn.execute(sql_call, {"p_id_clase": id_clase}) # Execute returns a ResultProxy

        return {"message": f"Clase con ID {id_clase} eliminada exitosamente."}

    except SQLAlchemyError as e:
        # Captura errores especificos de DB, incluyendo los de SIGNAL SQLSTATE
        print(f"Error de DB al ejecutar sp_EliminarClase para ID {id_clase}: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)

         # --- Manejo de errores SIGNAL de la DB ---
        # Captura mensajes de validacion/existencia definidos en el SP con SIGNAL '45000'
        if "Se requiere un ID de clase valido para eliminar." in error_mensaje_bd or \
           "La clase con el ID especificado no existe y no puede ser eliminada." in error_mensaje_bd: # Mensaje del SIGNAL para ID no existente
             return {"error": f"Error de validacion/existencia: {error_mensaje_bd}"}


        # Si no es un error SIGNAL conocido, devuelve el error generico de DB
        return {"error": f"Error al eliminar clase: {error_mensaje_bd}"}
    except Exception as e:
        # Captura cualquier otro error inesperado
        print(f"Error inesperado al ejecutar sp_EliminarClase para ID {id_clase}: {e}")
        return {"error": f"Ocurrio un error inesperado al eliminar la clase: {e}"}
    finally:
        if conn:
            try:
                conn.commit() # Confirma la eliminacion
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (eliminar_clase_sp): {e_close}")