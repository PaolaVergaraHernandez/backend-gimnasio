# utils.py

from sqlalchemy.orm import Session
from sqlalchemy import text # Importa text para ejecutar SQL plano

def ejecutar_stored_procedure(db: Session, sp_name: str, params: list = None):
    """
    Ejecuta un procedimiento almacenado que NO ESPERA resultados (INSERT, UPDATE, DELETE).
    """
    if params is None:
        params = []

    # Construye la llamada al procedimiento almacenado con placeholders para los parametros
    param_placeholders = ','.join([':param' + str(i) for i in range(len(params))])
    
    # Crea un diccionario de parametros para pasar a text()
    param_dict = {f'param{i}': param for i, param in enumerate(params)}

    # Construye la llamada SQL completa
    sql_call = text(f"CALL {sp_name}({param_placeholders})")

    # Ejecuta el procedimiento almacenado
    db.execute(sql_call, param_dict)


def ejecutar_stored_procedure_for_select(db: Session, sp_name: str, params: list = None):
    """
    Ejecuta un procedimiento almacenado que ESPERA resultados (SELECT).
    Retorna un objeto que puede ser usado con .fetchone() o .fetchall().
    """
    if params is None:
        params = []

    # Construye la llamada al procedimiento almacenado con placeholders para los parametros
    param_placeholders = ','.join([':param' + str(i) for i in range(len(params))])
    
    # Crea un diccionario de parametros para pasar a text()
    param_dict = {f'param{i}': param for i, param in enumerate(params)}

    # Construye la llamada SQL completa
    sql_call = text(f"CALL {sp_name}({param_placeholders})")

    # Ejecuta el procedimiento almacenado y retorna el resultado
    return db.execute(sql_call, param_dict)
