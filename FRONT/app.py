from flask import Flask, render_template,request,url_for,redirect

app = Flask(__name__)

# 1. Ruta del Panel Principal (Se activa al entrar a http://127.0.0.1:5000)
@app.route('/')
def panel_principal():
    return render_template('panel.html')

# 2. Ruta de la sección de Alumnos y Notas (Se activa al ir a /alumnos)
@app.route('/alumnos')
def seccion_alumnos():
    return render_template('alumnos.html')
@app.route('/grupos')
def seccion_grupos():
    nombre = request.args.get('nombre_profesor', '')
    return render_template('grupos.html', nombre_profesor=nombre)

@app.route('/grupo1')
def seccion_grupo1():
    return render_template('grupo1.html')
@app.route('/listado')
def seccion_listado():
    return render_template('listado.html')
if __name__ == '__main__':
    app.run(debug=True)
