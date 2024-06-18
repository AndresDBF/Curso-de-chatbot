from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

#Configuracion de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#modelo de la tabla log
class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#CREAR LA TABLA SI NO EXISTE
with app.app_context():
    db.create_all()
    
   
    
#Funcion para ordernar los registros por fecha y hora 
def ordernar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    #obtener todos los registros de la base de datos
    registros = Log.query.all()
    registros_ordenados = ordernar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)

mensajes_log = []

#funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)
    
    #guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#agregar_mensajes_log(json.dumps("Test1"))

#Token de verificacion para la configuracion
TOKEN_CURSO = 'CURSOWHATSAPP'



@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response


def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    
    if challenge and token == TOKEN_CURSO:
        return challenge
    else:
        return jsonify({'error': 'Token invalido'}),401
    
def recibir_mensajes(req):
    req = request.get_json()
    agregar_mensajes_log(req)
    
    return jsonify({'message':'EVENT_RECEIVED'})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80,debug=True)