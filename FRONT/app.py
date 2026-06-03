from flask import Flask, render_template,request,url_for,redirect
import requests

app = Flask(__name__)

@app.route('/buscar')
def buscar_seccion():

    texto = request.args.get('busqueda', '').lower()
    nombre = request.args.get('nombre_profesor', '')

    if 'usuario' in texto: #coloco en singular porque puede ser "usuarios" o "usuario"
        return render_template('usuarios.html',nombre_profesor=nombre)

    if 'alumno' in texto:
        return render_template('alumnos.html', nombre_profesor=nombre)

    if 'historial' in texto:
        return render_template('historial.html',nombre_profesor=nombre)

    if 'grupo' in texto:
        return render_template('grupos.html',nombre_profesor=nombre)

    if 'evaluacion' in texto:
        return render_template('registro_evaluaciones.html',nombre_profesor=nombre)

    if 'nota' in texto:
        return render_template('notas.html',nombre_profesor=nombre)

    if 'asistencia' in texto:
        return render_template('asistencias.html',nombre_profesor=nombre)

    return render_template('menu_principal.html', nombre_profesor=nombre, error_busqueda=True)

# 7. Ruta de la sección de Asistencias
@app.route('/asistencias')
def seccion_asistencias():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('asistencias.html', nombre_profesor=nombre)  

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

# 4. Ruta de la sección de Grupos
@app.route('/grupos')
def seccion_grupos():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('grupos.html', nombre_profesor=nombre)

# 3. Ruta de la sección de Historial
@app.route('/historial')
def seccion_historial():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('historial.html', nombre_profesor=nombre)

# 2. Ruta de la sección de Alumnos y Notas (Se activa al ir a /alumnos)
@app.route('/alumnos')
def seccion_alumnos():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('alumnos.html', nombre_profesor=nombre)

# 1. Ruta de la sección de Usuarios
@app.route('/usuarios')
def seccion_usuarios():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('usuarios.html', nombre_profesor=nombre)


# 0. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def inicio():
    return render_template('inicio.html')

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