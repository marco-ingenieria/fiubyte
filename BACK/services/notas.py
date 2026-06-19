from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)

def listar_notas(limit, offset):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = " SELECT n.ID, n.PADRON_ALUMNO,n.ID_EVALUACION, n.NOTA,e.NOMBRE AS NOMBRE_EVALUACION FROM NOTAS n JOIN EVALUACIONES e ON e.ID = n.ID_EVALUACION WHERE n.ELIMINADO = 0 LIMIT %s OFFSET %s "
        cursor.execute(select_stmt, [limit, offset])

        notas = cursor.fetchall()
        return construir_paginacion(notas, "/notas/", limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def listar_notas_padron(limit, offset, padron):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT n.ID,n.PADRON_ALUMNO,n.ID_EVALUACION,n.NOTA,e.NOMBRE AS NOMBRE_EVALUACION FROM NOTAS n JOIN EVALUACIONES e ON e.ID = n.ID_EVALUACION WHERE n.PADRON_ALUMNO = %s AND n.ELIMINADO = 0 LIMIT %s OFFSET %s "
        cursor.execute(select_stmt, [padron, limit, offset])

        notas = cursor.fetchall()
        return construir_paginacion(notas, "/notas/", limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def listar_notas_evaluacion(limit, offset, id_evaluacion):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT n.ID,n.PADRON_ALUMNO,n.ID_EVALUACION,n.NOTA,e.NOMBRE AS NOMBRE_EVALUACION FROM NOTAS n JOIN EVALUACIONES e ON e.ID = n.ID_EVALUACION WHERE n.ID_EVALUACION = %s AND n.ELIMINADO = 0 LIMIT %s OFFSET %s "
        cursor.execute(select_stmt, [id_evaluacion, limit, offset])

        notas = cursor.fetchall()
        return construir_paginacion(notas, "/notas/", limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def crear_nota(padron_alumno, id_evaluacion, nota):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO NOTAS (PADRON_ALUMNO, ID_EVALUACION, NOTA) VALUES(%s, %s, %s)"
        cursor.execute(create_stmt, [padron_alumno, id_evaluacion, nota])
        connection.commit()
        id_nota = cursor.lastrowid
        return (jsonify({"id": id_nota}), 201)
    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()