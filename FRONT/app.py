from flask import Flask, render_template,request

app = Flask(__name__)

# 3. Ruta de la sección de Usuarios
@app.route('/users')
def seccion_usuarios():
    return render_template('usuarios.html')

# 2. Ruta de la sección de Alumnos y Notas (Se activa al ir a /alumnos)
@app.route('/alumnos')
def seccion_alumnos():
    return render_template('alumnos.html')


# 1. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
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
