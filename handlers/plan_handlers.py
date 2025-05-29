# handlers/plan_handlers.py

from sqlalchemy import text # Para ejecutar SQL crudo
from sqlalchemy.exc import SQLAlchemyError # Importa el tipo base de error de SQLAlchemy
from database import engine # Importa el engine (AJUSTA LA RUTA SI ES NECESARIO si no esta en la raiz)
from decimal import Decimal # Para manejar Decimal en los resultados (precio)
# No necesitamos 'datetime' ni 'timedelta' porque la tabla planes ya no tiene TIMESTAMP


# --- Handler para sp_AgregarPlan ---
def agregar_plan_sp(
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
    duracion_dias: int
):
    """Ejecuta el procedimiento almacenado sp_AgregarPlan."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_AgregarPlan(:p_nombre, :p_descripcion, :p_precio, :p_duracion_dias)")
        conn.execute(sql_call, {
            "p_nombre": nombre, "p_descripcion": descripcion, "p_precio": precio,
            "p_duracion_dias": duracion_dias # Corregido el nombre del parametro a p_duracion_dias
        })
        conn.commit() # ¡IMPORTANTE! Confirmar la transaccion para guardar los cambios
        
        return {"mensaje": "Plan agregado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_AgregarPlan: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Error al agregar plan: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_AgregarPlan: {e}")
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Ocurrio un error inesperado al agregar plan: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (agregar_plan_sp): {e_close}")


# --- Handler para sp_ObtenerTodosPlanes ---
def obtener_todos_planes_sp(): # Nombre de la funcion corregido
    """Ejecuta el procedimiento almacenado sp_ObtenerTodosPlanes."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_ObtenerTodosPlanes()")

        lista_planes_dict = []
        with conn.execute(sql_call) as resultado:
            column_keys = resultado.keys()
            filas = resultado.fetchall()

        for fila in filas:
            plan_dict = dict(zip(column_keys, fila))

            # Convertir tipos de datos de DB a formatos compatibles con JSON
            if isinstance(plan_dict.get('precio'), Decimal):
                plan_dict['precio'] = str(plan_dict['precio']) # Convertir Decimal a string
            
            # Se elimina la logica para 'fecha_alta'
            
            lista_planes_dict.append(plan_dict)

        return lista_planes_dict # Devuelve la lista de diccionarios

    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ObtenerTodosPlanes: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        return {"error": f"Error al obtener todos los planes: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ObtenerTodosPlanes: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener todos los planes: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_todos_planes_sp): {e_close}")


# --- Handler para sp_ObtenerPlanPorID ---
def obtener_plan_por_id_sp(id_plan: int):
    """Ejecuta el procedimiento almacenado sp_ObtenerPlanPorID."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_ObtenerPlanPorID(:p_id_plan)")

        fila = None # Inicializa fila fuera del 'with'
        with conn.execute(sql_call, {"p_id_plan": id_plan}) as resultado:
            column_keys = resultado.keys()
            fila = resultado.fetchone() # Obtener la fila DENTRO del bloque 'with'

        # Procesar el resultado (la 'fila' ya fue obtenida antes de salir del 'with')
        if fila:
            plan_dict = dict(zip(column_keys, fila))

            # Convertir tipos de datos de DB a formatos compatibles con JSON
            if isinstance(plan_dict.get('precio'), Decimal):
                plan_dict['precio'] = str(plan_dict['precio']) # Convertir Decimal a string
            
            # Se elimina la logica para 'fecha_alta'
            
            return plan_dict # Devuelve el diccionario del plan
        else:
            # Si no se encontro ninguna fila, el plan no existe (o el ID no es valido)
            # Devolvemos un mensaje de no encontrada para que la ruta lo maneje
            return {"message": f"Plan con ID {id_plan} no encontrado."}

    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ObtenerPlanPorID: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        # Si el procedimiento usa SIGNAL SQLSTATE '45000' para ID invalido, el mensaje estara aqui.
        if "Se requiere un ID de plan valido." in error_mensaje_bd: # Mensaje del SIGNAL en el SP
            return {"error": "El ID de plan proporcionado no es valido."}
        return {"error": f"Error al obtener plan por ID: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ObtenerPlanPorID: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener plan por ID: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_plan_por_id_sp): {e_close}")


# --- Handler para sp_ActualizarPlan ---
def actualizar_plan_sp(
    id_plan: int,
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
    duracion_dias: int
):
    """Ejecuta el procedimiento almacenado sp_ActualizarPlan."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_ActualizarPlan(:p_id_plan, :p_nombre, :p_descripcion, :p_precio, :p_duracion_dias)")
        conn.execute(sql_call, {
            "p_id_plan": id_plan, "p_nombre": nombre, "p_descripcion": descripcion,
            "p_precio": precio, "p_duracion_dias": duracion_dias
        })
        conn.commit() # ¡IMPORTANTE! Confirmar la transaccion para guardar los cambios
        
        return {"mensaje": "Plan actualizado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ActualizarPlan: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Error al actualizar plan: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ActualizarPlan: {e}")
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Ocurrio un error inesperado al actualizar plan: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (actualizar_plan_sp): {e_close}")


# --- Handler para sp_EliminarPlan ---
def eliminar_plan_sp(id_plan: int):
    """Ejecuta el procedimiento almacenado sp_EliminarPlan."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_EliminarPlan(:p_id_plan)")
        conn.execute(sql_call, {"p_id_plan": id_plan})
        conn.commit() # ¡IMPORTANTE! Confirmar la transaccion para guardar los cambios
        
        return {"mensaje": "Plan eliminado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_EliminarPlan: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Error al eliminar plan: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_EliminarPlan: {e}")
        if conn:
            conn.rollback() # Revertir la transaccion en caso de error
        return {"error": f"Ocurrio un error inesperado al eliminar plan: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (eliminar_plan_sp): {e_close}")
