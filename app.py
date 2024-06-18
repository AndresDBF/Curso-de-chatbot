""" from flask import Flask, request, render_template, jsonify
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
TOKEN_CURSO = "CURSOWHATSAPP"



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
    app.run(host='0.0.0.0', port=80,debug=True) """

from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json
import http.client

app = Flask(__name__)

#Configuracion de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)

#Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#Crear la tabla si no existe
with app.app_context():
    db.create_all()

#Funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener todos los registros ed la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#Funcion para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    texto_str = json.dumps(texto)
    print("mensaje texto: ", texto)
    #Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto_str)
    print("nuevo registro: ", nuevo_registro)
    db.session.add(nuevo_registro)
    db.session.commit()

#Token de verificacion para la configuracion
TOKEN_ANDERCODE = "ANDERCODE"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        reponse = recibir_mensajes(request)
        return reponse

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error':'Token Invalido'}),401
def recibir_mensajes(req):
    print("el req: ", req)
    try:
        req_data = request.get_json()
        print("Datos JSON recibidos:", req_data)
        
        for entry in req_data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                for message in messages:
                    if "type" in message:
                        tipo = message["type"]
                        
                        if tipo == "interactive":
                            continue
                        if "text" in message:
                            text = message["text"]["body"]
                            numero = message["from"]
                            agregar_mensajes_log({"numero": numero})
                            agregar_mensajes_log({ "texto": text})

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return jsonify({'message': 'ERROR_PROCESSING_EVENT'}), 500

def enviar_mensajes_whatsapp(texto,numero):
    texto = texto.lower()
    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "text": {
                "preview_url": False,
                "body": "Hola como estas? bienvenido"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "text": {
                "preview_url": False,
                "body": "Hola como estas? bienvenido aqui estamos contestando desde el else."
            }
        }
    #convertir el diccionario a formato json
    data = json.dumps(data)  
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAARqlwZAqLocBO4oOz4JmZCrpxbhZCO2hEvPDJ1Wm0VGBZAz4MlLt3yDXWKkt2EzNSjZA4eXA9Hq4VWj9WeIvmhbis4XlvdHODSZCqHm572tMAnFiNZBlMxFqtC4Tz9ZBop8Tugn0xAnfWFTcwDOe5E3q62dTTpeFmx7eoG9PHlypkdphTVp6dbCCGy3xO4s5zJEzOxvto3w8dSSWagMaFIZD"
        
    }
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/373926142459719/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
        connection.close()

 

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)