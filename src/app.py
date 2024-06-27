from flask import Flask,jsonify
from flask_cors import CORS
import json

app = Flask(__name__)

CORS(app)

@app.route('/mapa', methods=['GET'])
def getMapa():
    with open('data/mapa.json', 'r') as file:
        datos = json.load(file)
        print("Datos leídos:", datos)
    return jsonify(datos)

@app.route('/sensores', methods=['GET'])
def getSensores():
    with open('data/sensores.json', 'r') as file:
        datos = json.load(file)
        print("Datos leídos:", datos)
    return jsonify(datos)

if __name__ == "__main__":
    app.run(debug=True)