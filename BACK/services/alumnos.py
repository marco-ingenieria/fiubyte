from io import BytesIO
from flask import jsonify, send_file
from db.init_db import get_connection
from utils import (construir_paginacion, construir_error, pdf_listado_alumnos)
import traceback

def listar_alumnos(limit, offset, base_url):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = """
            SELECT A.*, M.NOMBRE_MATERIA 
            FROM ALUMNOS A 
            INNER JOIN MATERIAS M ON A.ID_CURSO = M.ID 
            WHERE A.ELIMINADO = 0 
            ORDER BY A.PADRON 
            LIMIT %s OFFSET %s
        """
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

def listar_alumno_curso(limit, offset, base_url, id_curso):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        select_stmt = """
                    SELECT A.*, M.NOMBRE_MATERIA 
                    FROM ALUMNOS A 
                    INNER JOIN MATERIAS M ON A.ID_CURSO = M.ID 
                    WHERE A.ELIMINADO = 0 AND A.ID_CURSO = %s 
                    ORDER BY A.PADRON 
                    LIMIT %s OFFSET %s
                """
        cursor.execute(select_stmt, [id_curso, limit, offset])
        alumnos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM ALUMNOS WHERE ELIMINADO = 0 AND ID_CURSO = %s", [id_curso])
        total = cursor.fetchone()["total"]

        return construir_paginacion(alumnos, base_url, limit, offset, total)
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
        
        return alumno
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
    id_curso    = body.get("id_curso")
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        create_stmt = "INSERT INTO ALUMNOS (PADRON, NOMBRE, APELLIDO, MAIL, ID_CURSO, APROBO, ABANDONO) VALUES (%s, %s, %s, %s, %s, 0, 0)"
        cursor.execute(create_stmt, [padron, nombre, apellido, email, id_curso])

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
    aprobo      = body.get("aprobo")
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
        aprobo = alumno["APROBO"] if aprobo is None else aprobo
        abandono = alumno["ABANDONO"] if abandono is None else abandono

        if aprobo:
            abandono = False
        elif abandono:
            aprobo = False        

        update_stmt = """
        UPDATE ALUMNOS SET
        NOMBRE = %s,
        APELLIDO = %s,
        MAIL = %s,
        APROBO = %s,
        ABANDONO = %s
        WHERE PADRON = %s
        """
        cursor.execute(update_stmt, [nombre, apellido, email, aprobo, abandono, id])
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
        create_stmt = "INSERT INTO ALUMNOS (PADRON, NOMBRE, APELLIDO, MAIL, ID_CURSO, APROBO, ABANDONO) VALUES (%s, %s, %s, %s, %s, 0, 0)"

        for fila_bytes in csv:
            try:
                fila = fila_bytes.decode("utf-8")

                padron_raw, nombre_raw, apellido_raw, email_raw, id_curso_raw = tuple(fila.split(","))
                padron = int(padron_raw)
                nombre = nombre_raw.strip()
                apellido = apellido_raw.strip()
                email = email_raw.strip()
                id_curso = id_curso_raw.strip()
                datos_alumnos.append([padron, nombre, apellido, email, id_curso])
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

def listar_alumnos_pdf(padron, nombre, apellido, email, id_curso, aprobo, abandono):

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        columnas_seleccionadas = []

        if padron:
            columnas_seleccionadas.append("PADRON")
        if nombre:
            columnas_seleccionadas.append("NOMBRE")
        if apellido:
            columnas_seleccionadas.append("APELLIDO")
        if email:
            columnas_seleccionadas.append("MAIL")
        if id_curso:
            columnas_seleccionadas.append("ID_CURSO")
        if aprobo:
            columnas_seleccionadas.append("APROBO")
        if abandono:
            columnas_seleccionadas.append("ABANDONO")
        string_columnas = ", ".join(columnas_seleccionadas)

        select_stmt = f"SELECT {string_columnas} FROM ALUMNOS WHERE ELIMINADO = 0 ORDER BY ID_CURSO, PADRON"
        cursor.execute(select_stmt)

        encabezado = columnas_seleccionadas
        alumnos = cursor.fetchall()
        alumnos.insert(0, encabezado)
        
        pdf = pdf_listado_alumnos(alumnos)

        if pdf:
            respuesta_pdf = send_file(
                BytesIO(pdf),
                mimetype="application/pdf",
                as_attachment=True,
                download_name="listado_alumnos.pdf"
            )

            return respuesta_pdf
        else:
            return construir_error(500, "Error construyendo el pdf")
    except Exception as e:
        traceback.print_exc()

        return construir_error(500, f"Error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()