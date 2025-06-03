# handlers/producto_handlers.py

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import engine
from decimal import Decimal

# --- Handler para sp_AgregarProducto ---
def agregar_producto_sp(
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
    stock: int,
    imagen_url: str | None # ¡Añadimos imagen_url como parámetro!
):
    """Ejecuta el procedimiento almacenado sp_AgregarProducto."""
    conn = None
    try:
        conn = engine.connect()
        # Modificamos la llamada al SP para incluir el nuevo parámetro
        sql_call = text("CALL sp_AgregarProducto(:p_nombre, :p_descripcion, :p_precio, :p_stock, :p_imagen_url)")
        conn.execute(sql_call, {
            "p_nombre": nombre,
            "p_descripcion": descripcion,
            "p_precio": precio,
            "p_stock": stock,
            "p_imagen_url": imagen_url # ¡Pasamos el nuevo parámetro!
        })
        conn.commit() # ¡IMPORTANTE! Confirmar la transaccion para guardar los cambios
        
        return {"mensaje": "Producto agregado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_AgregarProducto: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback()
        return {"error": f"Error al agregar producto: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_AgregarProducto: {e}")
        if conn:
            conn.rollback()
        return {"error": f"Ocurrio un error inesperado al agregar producto: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (agregar_producto_sp): {e_close}")


# --- Handler para sp_ObtenerTodosProductos ---
def obtener_todos_productos_sp():
    """Ejecuta el procedimiento almacenado sp_ObtenerTodosProductos."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_ObtenerTodosProductos()")

        lista_productos_dict = []
        with conn.execute(sql_call) as resultado:
            column_keys = resultado.keys()
            filas = resultado.fetchall()

        for fila in filas:
            producto_dict = dict(zip(column_keys, fila))

            # Convertir tipos de datos de DB a formatos compatibles con JSON
            if isinstance(producto_dict.get('precio'), Decimal):
                producto_dict['precio'] = str(producto_dict['precio']) # Convertir Decimal a string
            
            # Asegurarse de que imagen_url esté presente (aunque sea None)
            # o manejarla si no la devuelve el SP (lo ideal es que sí la devuelva)
            # Si tu SP la devuelve, no necesitas esta línea, pero la dejo como seguridad.
            # Si tu SP ya devuelve 'imagen_url', esta línea no causa problema.
            producto_dict['imagen_url'] = producto_dict.get('imagen_url') 
            
            lista_productos_dict.append(producto_dict)

        return lista_productos_dict

    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ObtenerTodosProductos: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        return {"error": f"Error al obtener todos los productos: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ObtenerTodosProductos: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener todos los productos: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_todos_productos_sp): {e_close}")


# --- Handler para sp_ObtenerProductoPorID ---
def obtener_producto_por_id_sp(id_producto: int):
    """Ejecuta el procedimiento almacenado sp_ObtenerProductoPorID."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_ObtenerProductoPorID(:p_id_producto)")

        fila = None
        with conn.execute(sql_call, {"p_id_producto": id_producto}) as resultado:
            column_keys = resultado.keys()
            fila = resultado.fetchone()

        if fila:
            producto_dict = dict(zip(column_keys, fila))

            if isinstance(producto_dict.get('precio'), Decimal):
                producto_dict['precio'] = str(producto_dict['precio'])
            
            # Asegurarse de que imagen_url esté presente
            producto_dict['imagen_url'] = producto_dict.get('imagen_url')

            return producto_dict
        else:
            return {"message": f"Producto con ID {id_producto} no encontrado."}

    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ObtenerProductoPorID: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if "Se requiere un ID de producto valido." in error_mensaje_bd:
            return {"error": "El ID de producto proporcionado no es valido."}
        return {"error": f"Error al obtener producto por ID: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ObtenerProductoPorID: {e}")
        return {"error": f"Ocurrio un error inesperado al obtener producto por ID: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (obtener_producto_por_id_sp): {e_close}")


# --- Handler para sp_ActualizarProducto ---
def actualizar_producto_sp(
    id_producto: int,
    nombre: str,
    descripcion: str | None,
    precio: Decimal,
    stock: int,
    imagen_url: str | None # ¡Añadimos imagen_url como parámetro!
):
    """Ejecuta el procedimiento almacenado sp_ActualizarProducto."""
    conn = None
    try:
        conn = engine.connect()
        # Modificamos la llamada al SP para incluir el nuevo parámetro
        sql_call = text("CALL sp_ActualizarProducto(:p_id_producto, :p_nombre, :p_descripcion, :p_precio, :p_stock, :p_imagen_url)")
        conn.execute(sql_call, {
            "p_id_producto": id_producto,
            "p_nombre": nombre,
            "p_descripcion": descripcion,
            "p_precio": precio,
            "p_stock": stock,
            "p_imagen_url": imagen_url # ¡Pasamos el nuevo parámetro!
        })
        conn.commit()
        
        return {"mensaje": "Producto actualizado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_ActualizarProducto: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback()
        return {"error": f"Error al actualizar producto: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_ActualizarProducto: {e}")
        if conn:
            conn.rollback()
        return {"error": f"Ocurrio un error inesperado al actualizar producto: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (actualizar_producto_sp): {e_close}")


# --- Handler para sp_EliminarProducto ---
def eliminar_producto_sp(id_producto: int):
    """Ejecuta el procedimiento almacenado sp_EliminarProducto."""
    conn = None
    try:
        conn = engine.connect()
        sql_call = text("CALL sp_EliminarProducto(:p_id_producto)")
        conn.execute(sql_call, {"p_id_producto": id_producto})
        conn.commit()
        
        return {"mensaje": "Producto eliminado con exito"}
    except SQLAlchemyError as e:
        print(f"Error de DB al ejecutar sp_EliminarProducto: {e}")
        error_mensaje_bd = str(e.orig) if hasattr(e, 'orig') and e.orig else str(e)
        if conn:
            conn.rollback()
        return {"error": f"Error al eliminar producto: {error_mensaje_bd}"}
    except Exception as e:
        print(f"Error inesperado al ejecutar sp_EliminarProducto: {e}")
        if conn:
            conn.rollback()
        return {"error": f"Ocurrio un error inesperado al eliminar producto: {e}"}
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e_close:
                print(f"Error al cerrar conexion (eliminar_producto_sp): {e_close}")