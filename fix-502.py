from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "La aplicación está funcionando correctamente."

@app.route('/.well-known/captain-identifier')
def captain_health_check():
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 