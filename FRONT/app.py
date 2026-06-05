from flask import Flask, render_template,request,url_for,request
from datetime import date, datetime

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

        fecha_obj = None

        if not fecha:
            error = "Fecha inválida"
        else:
            try:
                fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
                if fecha_obj.year < 2000:
                    error = "Fecha inválida"
            except ValueError:
                error = "Fecha inválida"


        if error is None:
                if not horario:
                    error = "Horario inválido"
                else:
                    try:
                        datetime.strptime(horario, "%H:%M")
                    except ValueError:
                        error = "Horario inválido"

        if error is None:
    
            if fecha_obj < date.today():
                estado = "Finalizada"
            elif fecha_obj == date.today():
                estado = "Actual"
            else:
                estado = "Próximamente"

            clases.append({
                "id": len(clases) + 1, #id autoincremental para cada clase
                "fecha": fecha_obj.strftime("%Y-%m-%d"),
                "tema": tema,
                "horario": horario,
                "docente1": request.form["docente1"],
                "docente2": request.form["docente2"],
                "docente3": request.form["docente3"],
                "estado": estado
            })
    orden=request.args.get("orden", "asc")
    clases_ordenadas = clases.copy()
    
    if orden == "asc":
        clases_ordenadas.sort(key=lambda clase: datetime.strptime(clase["fecha"], "%Y-%m-%d"))

    elif orden == "desc":
        clases_ordenadas.sort(key=lambda clase: datetime.strptime(clase["fecha"], "%Y-%m-%d"),reverse=True)
    elif orden == "actual":
        clases_actuales = []
        resto_clases = []
        for clase in clases_ordenadas:
            if clase["estado"] == "Actual":
                clases_actuales.append(clase)
            else:
                resto_clases.append(clase)
        clases_ordenadas = clases_actuales + resto_clases

    return render_template("asistencias.html",clases=clases_ordenadas,nombre_profesor=nombre, error=error)

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
@app.route('/users')
def seccion_usuarios():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('usuarios.html', nombre_profesor=nombre)


# 0. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        nombre = request.form["nombre_profesor"]

        return render_template(
            "menu_principal.html",
            nombre_profesor=nombre
        )

    return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True)
