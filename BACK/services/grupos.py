from flask import jsonify
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error, existe_en_bd)
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
        
        
        query = "SELECT * FROM GRUPOS WHERE ELIMINADO = 0 ORDER BY FECHA_CREACION DESC LIMIT %s OFFSET %s;"
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

        
        query = "SELECT * FROM GRUPOS WHERE ID=%s AND ELIMINADO = 0;"
        cursor.execute(query, [id])
        registro = cursor.fetchone()

        if not registro:
            return construir_error(404, "Grupo no encontrado")
        
        return (jsonify(registro), 200)
    
    except Exception:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def obtener_alumnos(id_grupo):
    connection = None
    cursor = None 

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        
        #existe grupo
        if not existe_en_bd(cursor, "GRUPOS", "ID", id_grupo):
            return construir_error(404, "Grupo no encontrado")
        
        query = "SELECT A.PADRON, A.NOMBRE, A.APELLIDO, A.MAIL FROM GRUPO_ALUMNO GA " \
        "INNER JOIN ALUMNOS A ON A.PADRON=GA.PADRON_ALUMNO " \
        "WHERE GA.ID_GRUPO=%s AND GA.ELIMINADO=0"
        cursor.execute(query, [id_grupo])

        registros = cursor.fetchall()

        return (jsonify(registros), 200)
    
    except Exception:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def crear_grupo(nombre_grupo):
    connection = None
    cursor = None 

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        query = "INSERT INTO GRUPOS (NOMBRE) VALUES(%s);"
        cursor.execute(query, [nombre_grupo])
        connection.commit()

        return (jsonify({
            "mensaje": "Creacion de grupo exitosa",
            "grupo": {""
                "ID": cursor.lastrowid,
                "NOMBRE": nombre_grupo}
        }), 200)
    
    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


######asignar_alumnos_a_grupo
def existen_alumnos(cursor, padrones_alumnos):
    for padron in padrones_alumnos:
        if not existe_en_bd(cursor, "ALUMNOS", "PADRON", padron["padron"]):
            return False
    return True


def insertar_alumnos(cursor, id_grupo, padrones_alumnos):
    alumnos_insertados = 0
    for padron in padrones_alumnos:
        query = "INSERT INTO GRUPO_ALUMNO " \
        "(ID_GRUPO, PADRON_ALUMNO) " \
        "VALUES(%s, %s)"
        cursor.execute(query, [id_grupo, padron["padron"]])
        alumnos_insertados+=1

    return alumnos_insertados

def asignar_alumnos_a_grupo(id_grupo, padrones_alumnos):
    connection = None
    cursor = None 
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        #existe grupo
        if not existe_en_bd(cursor, "GRUPOS", "ID", id_grupo):
            return construir_error(404, "Grupo no encontrado")
        
        #existe alumnos
        if not existen_alumnos(cursor, padrones_alumnos):
            return construir_error(404, "Uno o más padrones no corresponden a alumnos existentes")

        alumnos_insertados = insertar_alumnos(cursor, id_grupo, padrones_alumnos)
        
        connection.commit()
        response = f"Se agregaron {alumnos_insertados} alumnos, al grupo de id={id_grupo}"
        return (jsonify(response), 200)        

    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



def actualizar_grupo(id_grupo, nombre_grupo):
    connection = None
    cursor = None 
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        #existe grupo
        if not existe_en_bd(cursor, "GRUPOS", "ID", id_grupo):
            return construir_error(404, "Grupo no encontrado")
        
        #update GRUPOS
        query = "UPDATE GRUPOS SET NOMBRE=%s " \
        "WHERE ID=%s"
        cursor.execute(query, [nombre_grupo, id_grupo])


        connection.commit()   
        return (jsonify({
            "mensaje": f"Nombre de grupo actualizado con exito",
            "grupo": {""
                "ID": id_grupo,
                "NOMBRE": nombre_grupo}
        }), 200)
    
    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def eliminar_grupo(id_grupo):
    
    connection = None
    cursor = None 
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary = True)

        #existe grupo
        if not existe_en_bd(cursor, "GRUPOS", "ID", id_grupo):
            return construir_error(404, "Grupo no encontrado")
        
        #delete GRUPO
        query = "UPDATE GRUPOS SET ELIMINADO=1 " \
        "WHERE ID=%s"
        cursor.execute(query, [id_grupo])

        query = "UPDATE GRUPO_ALUMNO SET ELIMINADO=1 " \
        "WHERE ID_GRUPO=%s"
        cursor.execute(query, [id_grupo])

        connection.commit()
        return (jsonify(f"El grupo de id={id_grupo} ha sido borrado con exito"), 200)    

    except:
        traceback.print_exc()
        return construir_error(500, "Error inesperado del servidor")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
