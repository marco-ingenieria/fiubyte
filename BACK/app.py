from flask import Flask
from routes.alumnos import alumnos_bp
from routes.usuarios import usuarios_bp
from routes.evaluaciones import evaluaciones_bp
from routes.grupos import grupos_bp
from routes.historial import historiales_bp
from routes.notas import notas_bp
from routes.clases import clases_bp
from routes.materias import materias_bp
from routes.asistencias import asistencias_bp
app = Flask(__name__)

app.register_blueprint(alumnos_bp, url_prefix='/alumnos')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(evaluaciones_bp, url_prefix='/evaluaciones')
app.register_blueprint(grupos_bp, url_prefix='/grupos')
app.register_blueprint(historiales_bp, url_prefix='/historiales')
app.register_blueprint(notas_bp, url_prefix='/notas')
app.register_blueprint(clases_bp, url_prefix='/clases')
app.register_blueprint(materias_bp, url_prefix='/materias')
app.register_blueprint(asistencias_bp, url_prefix='/asistencias')

@app.route("/")
def index():
    return "Fiubyte API corriendo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)