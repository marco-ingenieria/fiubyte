from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)


def listar_usuarios(limit, offset):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM USUARIOS WHERE ELIMINADO = 0 LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        usuarios = cursor.fetchall()
        return construir_paginacion(usuarios, "/usuarios/", limit, offset)

    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
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
        select_stmt = "SELECT ID_USUARIO, NOMBRE FROM USUARIOS WHERE NOMBRE = %s AND PASS = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [nombre, contrasenia])

        usuario = cursor.fetchone()
        if not usuario:
            return construir_error(401, "Usuario o contraseña incorrectos")
        print(f"Bienvenido {usuario['NOMBRE']}", flush=True)
        return (jsonify({"usuario": usuario}), 200)
        
    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def crear_usuario(nombre, contrasenia):
    cursor = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO USUARIOS (NOMBRE, PASS) VALUES(%s, %s)"
        cursor.execute(create_stmt, [nombre, contrasenia])
        connection.commit()
        id_usuario = cursor.lastrowid
        return (jsonify({"id": id_usuario}), 201)
    except Exception as e:
        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()