from flask import jsonify, url_for
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error, enviar_mail_asistencia)
import traceback

def listar_asistencias(limit, offset, base_url, clase_id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = """
        SELECT
            ALUMNOS.PADRON,
            ALUMNOS.NOMBRE,
            ALUMNOS.APELLIDO,
            ALUMNOS.MAIL,
            ASISTENCIAS.ID AS ID_ASISTENCIA,
            ASISTENCIAS.FECHA_CREACION AS FECHA_ASISTENCIA,
            CASE WHEN ASISTENCIAS.ID IS NULL THEN 0 ELSE 1 END AS ASISTIO
        FROM ALUMNOS
        LEFT JOIN ASISTENCIAS
            ON PADRON_ALUMNO = PADRON
            AND ASISTENCIAS.ELIMINADO = 0
            AND ID_CLASE = %s
        WHERE ALUMNOS.ELIMINADO = 0
        ORDER BY ASISTIO DESC, PADRON
        LIMIT %s OFFSET %s
        """
        cursor.execute(select_stmt, [clase_id, limit, offset])

        alumnos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM ALUMNOS WHERE ELIMINADO = 0")
        total = cursor.fetchone()["total"]
        listado = construir_paginacion(alumnos, base_url, limit, offset, total)
        
        return listado
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def crear_asistencia(clase_id, padron):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CLASES WHERE ID = %s AND ELIMINADO = 0", [clase_id])
        if not cursor.fetchone():
            return construir_error(404, "La clase no existe")

        cursor.execute("SELECT * FROM ALUMNOS WHERE PADRON = %s AND ELIMINADO = 0", [padron])
        if not cursor.fetchone():
            return construir_error(404, "El alumno no existe")

        create_stmt = """
        INSERT INTO ASISTENCIAS (ID_CLASE, PADRON_ALUMNO)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE ELIMINADO = 0
        """
        cursor.execute(create_stmt, [clase_id, padron])

        id = cursor.lastrowid
        
        connection.commit()
        return (jsonify({"id": id, "message": "Asistencia registrada"}), 201)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def enviar_mails_asistencia(clase_id, id_curso=None, registro_base_url=None):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if id_curso:
            select_stmt = "SELECT * FROM ALUMNOS WHERE ELIMINADO = 0 AND MAIL IS NOT NULL AND MAIL <> '' AND ID_CURSO = %s"
            cursor.execute(select_stmt, [id_curso])
        else:
            select_stmt = "SELECT * FROM ALUMNOS WHERE ELIMINADO = 0 AND MAIL IS NOT NULL AND MAIL <> ''"
            cursor.execute(select_stmt)

        alumnos = cursor.fetchall()
        if id_curso and not alumnos:
            return construir_error(404, "No se encontraron alumnos con email en ese curso")

        select_stmt = "SELECT * FROM CLASES WHERE ELIMINADO = 0 AND ID = %s"
        cursor.execute(select_stmt, [clase_id])

        clase = cursor.fetchone()

        if not clase:
            return construir_error(404, "La clase no existe")

        enviados = 0
        for alumno in alumnos:
            mail = alumno.get("MAIL")
            padron = alumno.get("PADRON")
            if not mail or not padron:
                continue
            if registro_base_url:
                url = f"{registro_base_url.rstrip('/')}/asistencias/registro/{clase_id}?padron={padron}"
            else:
                url = url_for('asistencias.get_registrar_asistencia', clase_id=clase_id, padron=padron, _external=True)
            fecha = clase.get("FECHA", "--/--/----")
            enviar_mail_asistencia(url, fecha, mail)
            enviados += 1
        
        return (jsonify({"enviados": enviados}), 200)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
