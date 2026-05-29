from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

def inicializarBase():
    print("BASE DE DATOS INICIALIZADA")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(current_dir, "init_db.sql")

    with open(sql_file) as f:
        sql = f.read()

    # Primera conexion: crear la BD
    connection = mysql.connector.connect(
        host    = os.getenv("DB_HOST"),
        user    = os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD"),
        port    = os.getenv("DB_PORT")
    )
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
    connection.commit()
    cursor.close()
    connection.close()

    # Segunda conexion: crear las tablas
    connection = mysql.connector.connect(
        host    = os.getenv("DB_HOST"),
        user    = os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD"),
        port    = os.getenv("DB_PORT"),
        database= os.getenv("DB_NAME")
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

def get_connection():
    connection = mysql.connector.connect(
        host    = os.getenv("DB_HOST"),
        user    = os.getenv("DB_USER"),
        password= os.getenv("DB_PASSWORD"),
        port    = os.getenv("DB_PORT"),
        database= os.getenv("DB_NAME")
    )

    return connection