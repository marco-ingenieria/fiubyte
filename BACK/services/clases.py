from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)
import traceback
import json
from datetime import datetime


def listar_clases(limit, offset, base_url):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM CLASES WHERE ELIMINADO = 0 ORDER BY FECHA, ID LIMIT %s OFFSET %s"
        cursor.execute(select_stmt, [limit, offset])

        clases = cursor.fetchall()
        for clase in clases:
            if clase.get('HORARIO') is not None:
                clase['HORARIO'] = str(clase['HORARIO'])
        listado = construir_paginacion(clases, base_url, limit, offset)
        
        return listado
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def buscar_clase(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = "SELECT * FROM CLASES WHERE ID = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [id])

        clase = cursor.fetchone()
        if not clase:
            return construir_error(404, f"Clase no encontrada")
        
        if clase and clase.get('HORARIO') is not None:
            clase['HORARIO'] = str(clase['HORARIO'])        
        
        return (jsonify({"clase": clase}), 200)
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def crear_clase(body):
    connection = None
    cursor = None

    #en otro momento podriamos hacer que solo te deje elegir usuarios
    profesores      = body.get('profesores')
    fecha           = body.get('fecha')
    horario         = body.get('horario')
    tema            = body.get('tema')
    #materia         = body.get('id_materia')

    #parse a JSON
    profesores = json.dumps(profesores)
    #parse a fecha
    fecha = datetime.strptime(fecha, "%Y-%m-%d")
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO CLASES (PROFESORES, FECHA, HORARIO, TEMA) VALUES (%s, %s, %s, %s)"
        cursor.execute(create_stmt, [profesores, fecha, horario, tema])

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


def actualizar_clase(body, id):
    connection = None
    cursor = None

    profesores      = body.get('profesores')
    fecha           = body.get('fecha')
    tema            = body.get('tema')
    horario         = body.get('horario')

    # Convertimos a JSON string únicamente si la lista contiene profesores reales
    if profesores is not None and isinstance(profesores, list) and len(profesores) > 0:
        profesores_json = json.dumps(profesores)
    else:
        profesores_json = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        select_stmt = "SELECT * FROM CLASES WHERE ID = %s AND ELIMINADO = 0"
        cursor.execute(select_stmt, [id])
        clase = cursor.fetchone()
        
        if not clase:
            return construir_error(404, f"Clase no encontrada")
        
        # --- COMBINACIÓN TOTALMENTE REPARADA ---
        final_profesores = profesores_json if profesores_json is not None else clase["PROFESORES"]
        final_tema       = tema if (tema is not None and tema != "") else clase["TEMA"]
        final_horario    = horario if (horario is not None and horario != "") else clase["HORARIO"]

        # Evitamos mandar horas/segundos a una columna tipo DATE de SQL
        if fecha and fecha != "":
            final_fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        else:
            final_fecha = clase["FECHA"]

        update_stmt = """
        UPDATE CLASES SET
        PROFESORES = %s,
        FECHA = %s,
        TEMA = %s,
        HORARIO = %s
        WHERE ID = %s
        """
        cursor.execute(update_stmt, [final_profesores, final_fecha, final_tema, final_horario, id])
        filas_afectadas = cursor.rowcount

        cursor.execute(select_stmt, [id])
        clase_actualizada = cursor.fetchone()
        connection.commit()
        
        # Retorno exitoso en tu formato nativo
        return (jsonify({"filas afectadas": filas_afectadas, "clase_actualizada": clase_actualizada}), 200)

    except Exception as e:
        traceback.print_exc()
        return construir_error(500, f"Error inesperado de base de datos: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_clase(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "UPDATE CLASES SET ELIMINADO = 1 WHERE ID = %s AND ELIMINADO = 0"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró la clase")

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



def eliminar_clase_permanente(id):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        update_stmt = "DELETE FROM CLASES WHERE ID = %s"
        cursor.execute(update_stmt, [id])

        filas_afectadas = cursor.rowcount
        if filas_afectadas == 0:
            return construir_error(404, "No se encontró la clase")

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