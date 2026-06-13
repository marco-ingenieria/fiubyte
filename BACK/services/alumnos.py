from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)
import traceback


def listar_alumnos(limit, offset, base_url):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM ALUMNOS WHERE ELIMINADO = 0 ORDER BY PADRON LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        alumnos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM ALUMNOS WHERE ELIMINADO=0")
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



def buscar_alumno(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM ALUMNOS WHERE PADRON = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [id])

        alumno = cursor.fetchone()

        if not alumno:
            return construir_error(404, f"Alumno no encontrado")
        
        return (jsonify({"alumno": alumno}), 200)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def crear_alumno(body):
    connection = None
    cursor = None

    padron      = body.get("padron")
    nombre      = body.get("nombre")
    apellido    = body.get("apellido")
    email       = body.get("email")
    abandono    = body.get("abandono")


    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO ALUMNOS (PADRON, NOMBRE, APELLIDO, MAIL, ABANDONO) VALUES (%s, %s, %s, %s, 0)"
        cursor.execute(create_stmt, [padron, nombre, apellido, email])

        filas_afectadas = cursor.rowcount
        
        connection.commit()
        return (jsonify({"filas afectadas": filas_afectadas}), 201)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def actualizar_alumno(body, id):
    connection = None
    cursor = None

    nombre      = body.get("nombre")
    apellido    = body.get("apellido")
    email       = body.get("email")
    abandono    = body.get("abandono")

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        select_stmt = "SELECT * FROM ALUMNOS WHERE PADRON = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [id])
        alumno = cursor.fetchone()
        
        if not alumno:
            return construir_error(404, f"Alumno no encontrado")
        
        #rellenar datos que no vengan en el body
        nombre      = nombre    or alumno["NOMBRE"]
        apellido    = apellido  or alumno["APELLIDO"]
        email       = email     or alumno["MAIL"]
        abandono    = abandono  or alumno["ABANDONO"]

        update_stmt = """
        UPDATE ALUMNOS SET
        NOMBRE = %s,
        APELLIDO = %s,
        MAIL = %s,
        ABANDONO = %s
        WHERE PADRON = %s
        """
        cursor.execute(update_stmt, [nombre, apellido, email, abandono, id])
        filas_afectadas = cursor.rowcount

        cursor.execute(select_stmt, [id])
        alumno_actualizado = cursor.fetchone()
        connection.commit()
        return (jsonify({"filas afectadas": filas_afectadas, "alumno_actualizado": alumno_actualizado}), 200)

    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_alumno(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "UPDATE ALUMNOS SET ELIMINADO = 1 WHERE PADRON = %s AND ELIMINADO = 0"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró el alumno")

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




def eliminar_alumno_permanente(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "DELETE FROM ALUMNOS WHERE PADRON = %s"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró el alumno")

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



def crear_alumnos_csv(csv):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        datos_alumnos = []
        create_stmt = "INSERT INTO ALUMNOS (PADRON, NOMBRE, APELLIDO, MAIL, ABANDONO) VALUES (%s, %s, %s, %s, 0)"
        
        for fila_bytes in csv:
            try:
                fila = fila_bytes.decode("utf-8")

                padron_raw, nombre_raw, apellido_raw, email_raw = tuple(fila.split(","))
                padron = int(padron_raw)
                nombre = nombre_raw.strip()
                apellido = apellido_raw.strip()
                email = email_raw.strip()
                datos_alumnos.append([padron, nombre, apellido, email])
            except ValueError:
                continue
            
        if len(datos_alumnos) == 0:
            return construir_error(400, "Filas vacías en el archivo .csv")
        
        cursor.executemany(create_stmt, datos_alumnos)

        filas_afectadas = cursor.rowcount
        
        connection.commit()
        return (jsonify({"filas afectadas": filas_afectadas}), 201)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
