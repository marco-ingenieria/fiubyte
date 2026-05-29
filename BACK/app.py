from flask import Flask
from routes.alumnos import alumnos_bp 
app = Flask(__name__)

app.register_blueprint(alumnos_bp, url_prefix='/alumnos')

@app.route("/")
def index():    
    return "Fiubyte API corriendo"

if __name__ == "__main__":
    #terminar de entender por que se usa host "0.0.0.0"
    app.run(host="0.0.0.0", port=5000)
