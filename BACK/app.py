from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():    
    return "Fiubyte API corriendo"

if __name__ == "__main__":
    #terminar de entender por que se usa host "0.0.0.0"
    app.run(host="0.0.0.0", port=5000)
