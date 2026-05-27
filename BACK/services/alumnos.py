from flask import jsonify
from ..db.init_db import get_connection
from ..utils import (construir_paginacion, construir_error)


def listar_alumnos(limit, offset):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM alumnos LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        alumnos = cursor.fetchall()
        listado = construir_paginacion(alumnos, limit, offset)
        
        return (jsonify({"listado": listado}), 200)
    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def buscar_alumno(id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM alumnos WHERE id = %s"
        cursor.execute(select_stmt, [id])

        alumno = cursor.fetchone()
        return (jsonify({"alumno": alumno}), 200)
    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def crear_alumno(body):
    padron      = body.get('padron')
    nombre      = body.get('nombre')
    apellido    = body.get('apellido')
    email       = body.get('email')

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO alumnos (padron, nombre, apellido, email) VALUES (%s, %s, %s, %s) RETURNING id"
        cursor.execute(create_stmt, [padron, nombre, apellido, email])

        id = cursor.fetchone()
        return (jsonify({"id": id}), 201)
    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def actualizar_alumno(body, id):
    padron      = body.get('padron')
    nombre      = body.get('nombre')
    apellido    = body.get('apellido')
    email       = body.get('email')

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        select_stmt = "SELECT * FROM alumnos WHERE id = %s"
        cursor.execute(select_stmt, [id])
        alumno = cursor.fetchone()
        
        if not alumno:
            return construir_error(f"Alumno no encontrado", 404)
        
        #rellenar datos que no vengan en el body
        padron      = padron    or alumno["padron"]
        nombre      = nombre    or alumno["nombre"]
        apellido    = apellido  or alumno["apellido"]
        email       = email     or alumno["email"]

        update_stmt = """
        UPDATE alumnos SET
        padron = %s,
        nombre = %s,
        apellido = %s,
        email = %s
        WHERE id = %s
        """
        cursor.execute(update_stmt, [padron, nombre, apellido, email, id])
        filas_afectadas = cursor.rowcount

        cursor.execute(select_stmt, [id])
        alumno_actualizado = cursor.fetchone()
        return (jsonify({"filas afectadas": filas_afectadas, "alumno_actualizado": alumno_actualizado}), 200)

    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_alumno(id):
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "UPDATE alumnos SET eliminado = 1 WHERE id = %s"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            construir_error("No se encontró el alumno", 404)

        return (jsonify({"filas afectadas": filas_afectadas}), 204)
    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_alumno_permanente(id):
    pass