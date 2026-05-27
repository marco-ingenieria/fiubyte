import mysql.connector
import os

def inicializarBase():
    print("BASE DE DATOS INICIALIZADA")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(current_dir, "init_db.sql")

    with open(sql_file) as f:
        sql = f.read()

    # Primera conexion: crear la BD
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sql01",
        port=3306
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS TP_FUBYTE")
    connection.commit()
    cursor.close()
    connection.close()

    # Segunda conexion: crear las tablas
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sql01",
        port=3306,
        database="TP_FUBYTE"
    )
    cursor = connection.cursor()
    for statement in sql.split(";"):
        if statement.strip():
            print(statement)
            cursor.execute(statement)
            connection.commit()
            print("Query ejecutada")

    cursor.close()
    connection.close()