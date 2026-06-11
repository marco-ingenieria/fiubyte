from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error, existe_en_bd)
import traceback






def listar_materias(base_url, limit, offset):
    connection = None
    cursor = None
    
    try: 
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if not isinstance(limit, int) or not isinstance(offset, int):
            return construir_error(400, "limit y offset deben ser números")
        if limit <= 0 or offset < 0:
            return construir_error(400, "limit > 0, offset >= 0")
        
        
        query = "SELECT " \
        "NOMBRE_MATERIA, CUATRIMESTRE, ANIO " \
        "FROM MATERIAS WHERE ELIMINADO = 0 ORDER BY FECHA_CREACION DESC LIMIT %s OFFSET %s;"
        params =[limit, offset]
        cursor.execute(query, params)
        registros = cursor.fetchall()
        
        
        cursor.execute("SELECT COUNT(*) as total FROM MATERIAS WHERE ELIMINADO=0")
        total = cursor.fetchone()["total"]

        grupos = construir_paginacion(registros, base_url, limit, offset, total)
        return grupos
    
    except Exception:
        traceback.print_exc()
        return  construir_error(500, "Error inesperado del servidor")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


#crear_materia
def existe_materia(cursor, nombre_materia, cuatrimestre, anio):
    
    cursor.execute("SELECT * FROM MATERIAS WHERE NOMBRE_MATERIA=%s AND CUATRIMESTRE=%s AND ANIO=%s AND ELIMINADO=0;", 
                   [nombre_materia, cuatrimestre, anio])
    return cursor.fetchone() is not None  

def crear_si_no_existe(cursor, nombre_materia, cuatrimestre, anio):


    cursor.execute("SELECT * FROM MATERIAS WHERE NOMBRE_MATERIA=%s AND CUATRIMESTRE = %s AND ANIO=%s AND ELIMINADO=1;", 
                   [nombre_materia, cuatrimestre, anio])
    materia_eliminada = cursor.fetchone()
    
    if materia_eliminada is not None:
        cursor.execute("UPDATE MATERIAS SET ELIMINADO=0 WHERE ID=%s;", [materia_eliminada["ID"]]) 
        return materia_eliminada["ID"]
    else:
        cursor.execute("INSERT INTO MATERIAS (NOMBRE_MATERIA, CUATRIMESTRE, ANIO) VALUES(%s, %s, %s);", 
                       [nombre_materia, cuatrimestre, anio])
        return cursor.lastrowid


def crear_materia(nombre_materia, cuatrimestre, anio):
    connection = None
    cursor = None 

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        if(existe_materia(cursor, nombre_materia, cuatrimestre, anio)):
            return construir_error(400, "La materia que se intenta crear ya existe")

        materia_id  = crear_si_no_existe(cursor, nombre_materia, cuatrimestre, anio)
        connection.commit()

        return (jsonify({
            "mensaje": "Creacion de materia exitosa",
            "materia": {
                "ID": materia_id,
                "NOMBRE_MATERIA": nombre_materia,
                "CUATRIMESTRE": cuatrimestre, 
                "ANIO": anio
            }
        }), 201)
    
    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()   