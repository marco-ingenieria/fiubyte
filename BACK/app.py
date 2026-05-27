from flask import Flask
from db.init_db import inicializarBase
app = Flask(__name__)

@app.route("/")
def index():
    
    return "Fiubyte API corriendo"

if __name__ == "__main__":
    inicializarBase()
    #terminar de entender por que se usa host "0.0.0.0"
    app.run(host="0.0.0.0", port=5000)
