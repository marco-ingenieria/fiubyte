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
        
        select_stmt = "SELECT ID FROM NOTAS WHERE PADRON_ALUMNO = %s AND ID_EVALUACION = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [padron_alumno, id_evaluacion])
        existente = cursor.fetchone()

        if existente:
            update_stmt = "UPDATE NOTAS SET NOTA = %s WHERE ID = %s"
            cursor.execute(update_stmt, [nota, existente["ID"]])
            connection.commit()
            return (jsonify({"id": existente["ID"]}), 200)
        else:
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


def listar_planilla_notas(id_materia):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT ID, NOMBRE, TIPO FROM EVALUACIONES WHERE ID_MATERIA=%s AND ELIMINADO=0 ORDER BY FECHA_CREACION",
            [id_materia]
        )
        evaluaciones = cursor.fetchall()

        cursor.execute(
            "SELECT PADRON, NOMBRE, APELLIDO FROM ALUMNOS WHERE ELIMINADO=0 ORDER BY APELLIDO"
        )
        alumnos = cursor.fetchall()

        if evaluaciones:
            ids_eval = [ev["ID"] for ev in evaluaciones]
            placeholders = ",".join(["%s"] * len(ids_eval))
            cursor.execute(
                f"SELECT PADRON_ALUMNO, ID_EVALUACION, NOTA FROM NOTAS WHERE ID_EVALUACION IN ({placeholders}) AND ELIMINADO=0",
                ids_eval
            )
            notas = cursor.fetchall()
        else:
            notas = []

        notas_dict = {}
        for n in notas:
            padron = n["PADRON_ALUMNO"]
            notas_dict.setdefault(padron, {})[n["ID_EVALUACION"]] = n["NOTA"]

        for alumno in alumnos:
            alumno["notas"] = [
                notas_dict.get(alumno["PADRON"], {}).get(ev["ID"], "")
                for ev in evaluaciones
            ]

        return jsonify({
            "evaluaciones": evaluaciones,
            "alumnos": alumnos
        }), 200

    except Exception:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()