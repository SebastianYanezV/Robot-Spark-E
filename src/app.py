from flask import Flask,jsonify

app = Flask(__name__)

@app.route('/mapa', methods=['GET'])
def getMapa():
    return jsonify({"mapa":"..."})

@app.route('/sensores', methods=['GET'])
def getSensores():
    return jsonify({"sensores":"hola"})

if __name__ == "__main__":
    app.run(debug=True)