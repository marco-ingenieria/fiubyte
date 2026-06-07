from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)

def historial_completo(limit, offset, base_url):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM HISTORIAL WHERE ELIMINADO = 0 LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        registros = cursor.fetchall()
        return construir_paginacion(registros, base_url, limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def historial_usuario(limit, offset, base_url, id_user):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM HISTORIAL WHERE ID_USUARIO = %s AND ELIMINADO = 0 LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [id_user, limit, offset])

        registros = cursor.fetchall()
        return construir_paginacion(registros, base_url, limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def crear_registro(cursor, accion, descripcion, id_usuario):
    create_stmt = "INSERT INTO HISTORIAL (ACCION, DESCRIPCION, ID_USUARIO) VALUES(%s, %s, %s)"
    cursor.execute(create_stmt, [accion, descripcion, id_usuario])
    id_registro = cursor.lastrowid
    return id_registro



def eliminar_registro(id):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "UPDATE HISTORIAL SET ELIMINADO = 1 WHERE ID_REGISTRO = %s AND ELIMINADO = 0"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró el registro")

        connection.commit()
        return (jsonify({}), 204)
    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()