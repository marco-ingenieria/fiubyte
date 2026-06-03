from flask import Flask
from routes.alumnos import alumnos_bp
from routes.usuarios import usuarios_bp
from routes.evaluaciones import evaluaciones_bp
from routes.grupos import grupos_bp
app = Flask(__name__)

app.register_blueprint(alumnos_bp, url_prefix='/alumnos')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
app.register_blueprint(evaluaciones_bp, url_prefix='/evaluaciones')
app.register_blueprint(grupos_bp, url_prefix='/grupos')

@app.route("/")
def index():
    return "Fiubyte API corriendo"

if __name__ == "__main__":
    #terminar de entender por que se usa host "0.0.0.0"
    app.run(host="0.0.0.0", port=5000)
