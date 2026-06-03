from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error)
import traceback



def listar_grupos(base_url, limit, offset):
    connection = None
    cursor = None
    
    try: 
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if not isinstance(limit, int) or not isinstance(offset, int):
            return construir_error(400, "limit y offset deben ser números")
        if limit <= 0 or offset < 0:
            return construir_error(400, "limit > 0, offset >= 0")
        
        
        query = "SELECT * FROM GRUPOS ORDER BY FECHA_CREACION DESC LIMIT %s OFFSET %s;"
        params =[limit, offset]
        cursor.execute(query, params)
        registros = cursor.fetchall()

        grupos = construir_paginacion(registros, base_url, limit, offset)
        return grupos
    
    except Exception:
        traceback.print_exc()
        return  construir_error(500, "Error inesperado del servidor")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    


def obtener_grupo(id):
    connection = None
    cursor = None 

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM GRUPOS WHERE ID=%s;"
        cursor.execute(query, [id])
        registro = cursor.fetchone()

        return registro
    
    except Exception:

        traceback.print_exc()
        return  construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



