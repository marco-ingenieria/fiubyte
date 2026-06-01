from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)


def listar_usuarios(limit, offset):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM USUARIOS LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        usuarios = cursor.fetchall()
        return construir_paginacion(usuarios, "/usuarios/", limit, offset)

    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def chequear_usuario(nombre, contrasenia):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT ID_USUARIO, NOMBRE FROM USUARIOS WHERE NOMBRE = %s AND PASS = %s"
        cursor.execute(select_stmt, [nombre, contrasenia])

        usuario = cursor.fetchone()
        if not usuario:
            return construir_error(401, "Usuario o contraseña incorrectos")
        print(f"Bienvenido {usuario['NOMBRE']}", flush=True)
        return (jsonify({"usuario": usuario}), 200)
        
    except Exception as e:
        return construir_error(f"Error inesperado: {e}", 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()