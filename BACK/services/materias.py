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
        "NOMBRE_MATERIA, CUATRIMESTRE, ANIO, ID " \
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


def obtener_materia(id):
    connection = None
    cursor = None
    
    try: 
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * " \
        "FROM MATERIAS WHERE ELIMINADO = 0 AND ID=%s ORDER BY FECHA_CREACION DESC;"
        cursor.execute(query, [id])
        registro = cursor.fetchone()       
        
        if registro is None:
            return construir_error(404, f"La materia con id={id} no existe")
        
        return (jsonify(registro), 200)
    
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



def actualizar_materia(id, data):
    connection = None
    cursor = None
    
    try: 

        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        nombre_materia      = data.get("nombre_materia")
        cuatrimestre        = data.get("cuatrimestre")
        anio                = data.get("anio")

        query = "SELECT * " \
        "FROM MATERIAS WHERE ELIMINADO = 0 AND ID=%s ORDER BY FECHA_CREACION DESC;"
        cursor.execute(query, [id])
        registro = cursor.fetchone()       
        
        if registro is None:
            return construir_error(404, f"La materia con id={id} no existe")
        
    
        if not (cuatrimestre is None) and (not isinstance(cuatrimestre, int) or (cuatrimestre != 1 and cuatrimestre!=2)):
            return construir_error(400, "'cuatrimestre' debe ser el numero de valor 1 o de valor 2")
    
        if not (anio is None)and ( not isinstance(anio, int) or not (anio >= 2000 and anio <= 2100)):
            return construir_error(400, "'anio' debe ser el anio entre el rango [2000, 2100]")
        
        #agregar validaciones sobre los parametros??
        nombre_materia  = nombre_materia if nombre_materia is not None else registro["NOMBRE_MATERIA"]
        cuatrimestre    = cuatrimestre if cuatrimestre is not None else registro["CUATRIMESTRE"]
        anio            = anio if anio is not None else registro["ANIO"]

        query = "UPDATE MATERIAS SET " \
        "NOMBRE_MATERIA = %s, CUATRIMESTRE=%s, ANIO = %s " \
        "WHERE ID = %s"

        cursor.execute(query, [nombre_materia, cuatrimestre, anio, id ])
        connection.commit()

        return (jsonify({
                "filas_actualizadas": cursor.rowcount,
                "mensaje": "materia actualizada correctamente",
                "materia_actualizada": {
                "ID": id,
                "NOMBRE_MATERIA": nombre_materia,
                "CUATRIMESTRE": cuatrimestre,
                "ANIO": anio}}), 200)

    except Exception:
        traceback.print_exc()
        return  construir_error(500, "Error inesperado del servidor")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def eliminar_materia(id_materia):
    connection = None
    cursor = None 
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        #existe materia
        query = "SELECT * " \
        "FROM MATERIAS WHERE ELIMINADO = 0 AND ID=%s ORDER BY FECHA_CREACION DESC;"
        cursor.execute(query, [id_materia])
        registros = cursor.fetchall()       
        
        if registros is None:
            return construir_error(404, f"La materia con id={id_materia} no existe")
        
        
        query = "UPDATE MATERIAS SET ELIMINADO=1 WHERE ID = %s"
        cursor.execute(query, [id_materia])
        connection.commit()

        return (jsonify({
            "mensaje": "materia eliminada con éxito",
            "materias eliminadas" : registros
        }), 200)    

    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
