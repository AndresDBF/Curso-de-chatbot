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
                            enviar_mensajes_whatsapp(text, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return jsonify({'message': 'ERROR_PROCESSING_EVENT'}), 500

def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Hola, ¿cómo estás? Bienvenido"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Hola, ¿cómo estás? Aquí estamos contestando desde el else."
            }
        }
    
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAARqlwZAqLocBOZB6YKcQc6jOOIJx4kLogrwOYH2nlL6BUwQiU3ubcWXp4L9GZBZAOQVOApOVZC7kHkYvaSPtwLZBplQ81lRyQE6rkp8loaRA8ODH2APEhAtNNol99OMZCqXGqRCx5deXURsyhbK6dHT51GAZBclYZBGl4rih3CaQJcYyaubxQmVo4Svti5q4RGfD5NyadCxphGBPFEZAXrcFq3ZAcZD"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")
    
    try:
        connection.request("POST", "/v19.0/373926142459719/messages", data, headers)
        response = connection.getresponse()
        response_data = response.read().decode()
        print(response.status, response.reason, response_data)
        if response.status != 200:
            agregar_mensajes_log(f"Error al enviar mensaje: {response.status} {response.reason} {response_data}")
    except Exception as e:
        print(f"Exception: {e}")
        agregar_mensajes_log(f"Exception al enviar mensaje: {e}")
    finally:
        connection.close()
 

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)