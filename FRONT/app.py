from flask import Flask, render_template,request,url_for,redirect
import requests
from datetime import date, datetime
import json

app = Flask(__name__)

@app.route('/buscar')
def buscar_seccion():

    nombre = request.args.get('nombre_profesor', '')

    texto = request.args.get('busqueda', '').lower().strip()

    if texto.startswith('usuario'):
        return redirect(url_for('seccion_usuarios',nombre_profesor=nombre))

    if texto.startswith('alumno'):
        return redirect(url_for('seccion_alumnos', nombre_profesor=nombre))

    if texto.startswith('historial'):
        return redirect(url_for('seccion_historial',nombre_profesor=nombre))

    if texto.startswith('grupo'):
        return redirect(url_for('seccion_grupos', nombre_profesor=nombre))

    if texto.startswith('evaluacion'):
        return redirect(url_for('seccion_evaluaciones',nombre_profesor=nombre))

    if texto.startswith('nota'):
        return redirect(url_for('seccion_notas',nombre_profesor=nombre))

    if texto.startswith('asistencia'):
        return redirect(url_for('seccion_asistencias',nombre_profesor=nombre))

    return redirect(url_for('menu_principal', nombre_profesor=nombre, error_busqueda=True))

# 8. Ruta para mostrar el perfil del alumno

@app.route("/alumno")
def perfil_alumno():

    alumno = {    #REEMPLZAR POR DATOS SQL REALES
        "nombre": "Juan Pérez",
        "asistencias": 87,
        "promedio": 8.4,
        "padron": 109876,
        "grupos": ["Grupo 1", "Grupo 3"],
        "trabajos": 5,
        "notas": [9, 8, 7, 10]
    }

    return render_template(
        "alumno.html",
        alumno=alumno
    )

#7. Ruta para mostrar el QR de la clase actual

@app.route("/qr")
def mostrar_qr():
    id_clase = int(request.args.get("id"))
    clase_encontrada = None

    for clase in clases:
        if clase["id"] == id_clase:
            clase_encontrada = clase

    return render_template("qr.html",clase=clase_encontrada)

# 7. Ruta de la sección de Asistencias

clases = [] #la idea de dejarla afuera es para q acumule las clses agregadas, si la dejo adentro se reinicia cada vez que se hace un POST

@app.route("/asistencias", methods=["GET", "POST"])
def seccion_asistencias():
    nombre = request.args.get('nombre_profesor', '')
    error = None

    if request.method == "POST":
        fecha = request.form.get("fecha")
        tema = request.form.get("tema")
        horario = request.form.get("horario")
        docente1 = request.form.get("docente1", "")
        docente2 = request.form.get("docente2", "")
        docente3 = request.form.get("docente3", "")
        profesores = [d for d in [docente1, docente2, docente3] if d]

        try:
            requests.post("http://backend:5000/clases/", json={
                "profesores": profesores,
                "fecha": fecha,
                "horario": horario,
                "tema": tema
            })
        except Exception as e:
            error = "No se pudo conectar al servidor"

    try:
        response = requests.get("http://backend:5000/clases/", params={"limit": 100, "offset": 0})
        clases_raw = response.json().get("listado", [])
    except Exception as e:
        clases_raw = []

    clases = []
    for c in clases_raw:
        try:
            fecha_obj = datetime.strptime(c.get("FECHA", ""), "%a, %d %b %Y %H:%M:%S %Z").date()
            fecha_str = fecha_obj.strftime("%Y-%m-%d")
            if fecha_obj < date.today():
                estado = "Finalizada"
            elif fecha_obj == date.today():
                estado = "Actual"
            else:
                estado = "Próximamente"
        except:
            estado = "Desconocido"
            fecha_str = ""

        try:
            profesores_lista = json.loads(c.get("PROFESORES", "[]"))
        except:
            profesores_lista = []

        clases.append({
            "id": c.get("ID"),
            "fecha": fecha_str,
            "tema": c.get("TEMA", ""),
            "horario": str(c.get("HORARIO", "")),
            "docente1": profesores_lista[0] if len(profesores_lista) > 0 else "",
            "docente2": profesores_lista[1] if len(profesores_lista) > 1 else "",
            "docente3": profesores_lista[2] if len(profesores_lista) > 2 else "",
            "estado": estado
        })

    orden = request.args.get("orden", "asc")
    if orden == "asc":
        clases.sort(key=lambda c: c["fecha"])
    elif orden == "desc":
        clases.sort(key=lambda c: c["fecha"], reverse=True)
    elif orden == "actual":
        clases_actuales = [c for c in clases if c["estado"] == "Actual"]
        resto = [c for c in clases if c["estado"] != "Actual"]
        clases = clases_actuales + resto

    return render_template("asistencias.html", clases=clases, nombre_profesor=nombre, error=error)

@app.route('/editar_clase/<int:id>', methods=['POST'])
def editar_clase(id):
    docente1 = request.form.get('docente1', '')
    docente2 = request.form.get('docente2', '')
    docente3 = request.form.get('docente3', '')
    profesores = [d for d in [docente1, docente2, docente3] if d]
    try:
        requests.patch(f"http://backend:5000/clases/{id}", json={
            "profesores": profesores,
            "fecha": request.form.get('fecha'),
            "horario": request.form.get('horario'),
            "tema": request.form.get('tema')
        })
    except Exception as e:
        pass
    return redirect(url_for('seccion_asistencias'))

@app.route('/eliminar_clase/<int:id>', methods=['POST'])
def eliminar_clase(id):
    try:
        requests.delete(f"http://backend:5000/clases/{id}")
    except Exception as e:
        pass
    return redirect(url_for('seccion_asistencias'))

# 6. Ruta de la sección de Notas
@app.route('/notas')
def seccion_notas():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('notas.html', nombre_profesor=nombre)

# 5. Ruta de la sección de Evaluaciones
@app.route('/evaluaciones')
def seccion_evaluaciones():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('registro_evaluaciones.html', nombre_profesor=nombre)

@app.route('/grupos', methods=["POST", "GET"])
def seccion_grupos():
    nombre_profesor = request.args.get('nombre_profesor', '')
    padron_asignar = request.form.get('padron_asignar')
    grupo_id = request.form.get('grupo_id')
 
    if request.method == "POST":
        crear = request.form.get('crear')
        eliminar = request.form.get('eliminar')

        if eliminar:
            try:
                requests.delete(f"http://backend:5000/grupos/{eliminar}")
            except Exception as e:
                print("Error al eliminar grupo")
        elif crear:
            try:
                requests.post("http://backend:5000/grupos/", json={
                    "nombre": crear
                })
            except Exception as e:
                print("Error al crear grupo")
        elif padron_asignar and grupo_id:
            try:
                requests.post(f"http://backend:5000/grupos/asignar-alumnos", json={
            "id_grupo": int(grupo_id),
            "padrones_alumnos": [{"padron": int(padron_asignar)}]
                })
            except Exception as e:
                print("Error al asignar alumno ")

    grupos = []
    try:
        response = requests.get("http://backend:5000/grupos/", params={"limit": 30, "offset": 0})
        grupos = response.json().get("listado", [])
    except Exception as e:
        print("Hubo un error")

    return render_template('grupos.html', nombre_profesor=nombre_profesor, grupos=grupos)

# NUEVA RUTA: Hoja de detalle de un grupo específico (Accedida desde el perfil o listados)
@app.route('/grupo-detalle')
def detalle_grupo_especifico():
    nombre_profesor = request.args.get('nombre_profesor', '')
    
    # Atajamos cuál grupo exacto se quiere ver (ej: "Grupo 1")
    id_grupo = request.args.get('id', '')

    # =========================================================================
    # LÓGICA SQL FUTURA:
    # # 1. Buscamos los datos de este grupo en la base de datos:
    # grupo_datos = db.execute("SELECT * FROM grupos WHERE nombre = ?", id_grupo)
    #
    # # 2. Buscamos a todos los alumnos que pertenecen a este grupo para listarlos:
    # integrantes = db.execute("SELECT nombre, padron FROM alumnos WHERE grupo = ?", id_grupo)
    # =========================================================================

    # Datos fijos temporales para que no tire error al renderizar mientras desarrollás
    grupo_simulado = {
        "nombre": id_grupo if id_grupo else "Grupo Sin Nombre",
        "materia": "Diseño de Sistemas",
        "integrantes": ["Juan Pérez", "Ana Gómez", "Lucas Díaz"]
    }

    return render_template(
        'grupo_individual.html', # Esta es la nueva plantilla física para la hoja del grupo
        nombre_profesor=nombre_profesor,
        grupo=grupo_simulado
    )

# 2. Ruta de la sección de Alumnos y Notas (Se activa al ir a /alumnos)
@app.route('/alumnos', methods=["POST","GET"])
def seccion_alumnos():
    nombre = request.args.get('nombre_profesor', '')
    crear_alumno = request.form.get('crear_alumno')
    eliminar_alumno = request.form.get('eliminar_alumno')
    if crear_alumno:
        try:
            requests.post("http://backend:5000/alumnos/", json={
                "nombre": request.form.get('crear_alumno'),
                "apellido": request.form.get('apellido'),
                "email": request.form.get('email'),
                "padron": request.form.get('padron')
            })
        except Exception as e:
            print("Error al crear alumno")

    if eliminar_alumno:
        try:
            requests.delete(f"http://backend:5000/alumnos/{eliminar_alumno}")
        except Exception as e:
            print("Error al eliminar alumno")
    try:
        response = requests.get("http://backend:5000/alumnos/")
        alumnos = response.json().get("listado", [])
    except Exception as e:
        alumnos = []

    return render_template('alumnos.html', nombre_profesor=nombre, alumnos=alumnos)

# 1. Ruta de la sección de Usuarios
@app.route('/usuarios')
def seccion_usuarios():
    nombre = request.args.get('nombre_profesor', '')
    try:
        response = requests.get("http://backend:5000/usuarios/", params={"limit": 30, "offset": 0})
        usuarios = response.json().get("listado", [])
    except Exception as e:
        usuarios = []
    return render_template('usuarios.html', nombre_profesor=nombre, usuarios=usuarios)

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    nombre_profesor = request.args.get('nombre_profesor', '')
    nombre = request.form.get('nombre')
    contrasenia = request.form.get('contrasenia')
    try:
        requests.post("http://backend:5000/usuarios/", json={
            "nombre": nombre,
            "contrasenia": contrasenia
        })
    except Exception as e:
        pass
    return redirect(url_for('seccion_usuarios',nombre_profesor=nombre_profesor))

@app.route('/eliminar_usuario', methods=['POST'])
def eliminar_usuario():
    nombre_profesor = request.args.get('nombre_profesor', '')
    id = request.form.get('eliminar-usuario-id')
    try:
        requests.delete(f"http://backend:5000/usuarios/{id}")
    except Exception as e:
        pass
    return redirect(url_for('seccion_usuarios',nombre_profesor=nombre_profesor))


# 0. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/menu')
def menu_principal():
    nombre = request.args.get('nombre_profesor', '')
    error_busqueda = request.args.get('error_busqueda')
    return render_template('menu_principal.html',nombre_profesor=nombre, error_busqueda=error_busqueda)

#Modifique un toque para pasar contrasenia aparte de nombre al back
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form["nombre_profesor"]
        password = request.form["password"]
        try:
            response = requests.post("http://backend:5000/usuarios/login", json={
                "nombre": nombre,
                "contrasenia": password
            })
            if response.status_code == 200:
                return render_template("menu_principal.html", nombre_profesor=nombre)
            else:
                return render_template("login.html", error="Usuario o contraseña incorrectos")
        except Exception as e:
            return render_template("login.html", error="No se pudo conectar al servidor")
    return render_template("login.html")

@app.route('/grupo/<int:id>', methods=["GET", "POST"])
def ver_grupo(id):
    nombre = request.args.get('nombre_profesor', '')
    lista_alumnos = [] 
    if request.method == "POST":   
        eliminar_alumno= request.form.get('eliminar')
        if eliminar_alumno:
            try:
                requests.delete(f"http://backend:5000/grupos/{id}/alumnos/{eliminar_alumno}")
            except Exception as e:
                print("Error al eliminar alumno del grupo")

    try:
        response = requests.get(f"http://backend:5000/grupos/alumnos/{id}")
        lista_alumnos = response.json()
    except Exception as e:
        print('Hubo un error al obtener los alumnos del grupo')
    return render_template('detalle_grupo.html',nombre=nombre, integrantes=lista_alumnos,nombre_profesor=nombre,ID=id)
@app.route('/listado')
def seccion_listado():
    return render_template('listado.html')
if __name__ == '__main__':
    app.run(debug=True)
