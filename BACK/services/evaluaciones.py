from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)
import traceback


def listar_evaluaciones(limit, offset, base_url):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM EVALUACIONES ORDER BY ID_MATERIA, FECHA_CREACION, ID LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        evaluaciones = cursor.fetchall()
        listado = construir_paginacion(evaluaciones, base_url, limit, offset)
        
        return listado
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def buscar_evaluacion(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM EVALUACIONES WHERE ID = %s"
        cursor.execute(select_stmt, [id])

        evaluacion = cursor.fetchone()

        if not evaluacion:
            return construir_error(404, f"Evaluación no encontrada")
        
        return (jsonify({"evaluacion": evaluacion}), 200)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def crear_evaluacion(body):
    connection = None
    cursor = None

    tipo        = body.get('tipo')
    nombre      = body.get('nombre')
    materia     = body.get('id_materia')

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO EVALUACIONES (TIPO, NOMBRE, ID_MATERIA) VALUES (%s, %s, %s)"
        cursor.execute(create_stmt, [tipo, nombre, materia])

        id = cursor.lastrowid
        
        connection.commit()
        return (jsonify({"id": id}), 201)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def actualizar_evaluacion(body, id):
    connection = None
    cursor = None

    tipo        = body.get('tipo')
    nombre      = body.get('nombre')

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        select_stmt = "SELECT * FROM EVALUACIONES WHERE ID = %s"
        cursor.execute(select_stmt, [id])
        evaluacion = cursor.fetchone()
        
        if not evaluacion:
            return construir_error(404, f"Evaluación no encontrada")
        
        #rellenar datos que no vengan en el body
        nombre      = nombre    or evaluacion["NOMBRE"]
        tipo        = tipo      or evaluacion["TIPO"]

        update_stmt = """
        UPDATE EVALUACIONES SET
        NOMBRE = %s,
        TIPO = %s
        WHERE ID = %s
        """
        cursor.execute(update_stmt, [nombre, tipo, id])
        filas_afectadas = cursor.rowcount

        cursor.execute(select_stmt, [id])
        evaluacion_actualizada = cursor.fetchone()
        connection.commit()
        return (jsonify({"filas afectadas": filas_afectadas, "evaluacion_actualizada": evaluacion_actualizada}), 200)

    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_evaluacion(id):
    connection = None
    cursor = None
    # try:
    #     connection = get_connection()
    #     cursor = connection.cursor(dictionary=True)

    #     update_stmt = "UPDATE EVALUACIONES SET ELIMINADO = 1 WHERE ID = %s"
    #     cursor.execute(update_stmt, [id])

    #     filas_afectadas = cursor.rowcount
    #     if filas_afectadas == 0:
    #         return construir_error(404, "No se encontró la evaluación")

    #     connection.commit()
    #     return (jsonify({}), 204)
    # except Exception as e:
    #     traceback.print_exc()
        
    #     return construir_error(500, f"Error inesperado: {e}")
    # finally:
    #     if cursor:
    #         cursor.close()
    #     if connection and connection.is_connected():
    #         connection.close()



def eliminar_evaluacion_permanente(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "DELETE FROM EVALUACIONES WHERE ID = %s"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró la evaluación")

        connection.commit()
        return (jsonify({}), 204)
    except Exception as e:
        traceback.print_exc()
        
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()