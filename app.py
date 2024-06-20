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
                        agregar_mensajes_log({"tipo": tipo})
                        agregar_mensajes_log({"mensaje": message})
                        if tipo == "interactive":
                            tipo_interactivo = message["interactive"]["type"]
                            if tipo_interactivo == "button_reply":
                                text = message["interactive"]["button_reply"]["id"]
                                numero = message["from"]
                                enviar_mensajes_whatsapp(text, numero)
                            elif tipo_interactivo == "list_reply":
                                text = message["interactive"]["list_reply"]["id"]
                                numero = message["from"]

                                enviar_mensajes_whatsapp(text,numero)
                        if "text" in message:
                            text = message["text"]["body"]
                            numero = message["from"]
                            
                            enviar_mensajes_whatsapp(text, numero)
                            agregar_mensajes_log({"mensaje": message})
        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print("Error al procesar el mensaje:", e)
        return jsonify({'message': 'ERROR_PROCESSING_EVENT'}), 500

def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower()
    if texto in ["hola", "buenas", "buenos", "como estás", "como estas", "cómo estas", "cómo estás?", "cómo estás"]:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "🚀Hola, somo Poseidon 🔱 la empresa líder en productos textiles de Venezuela información \n 📌Por favor, ingresa un número #️⃣ para recibir información. \n 1️⃣ Información del pedido. ❔ \n 2️⃣ Ubicaciónes en el país📍 \n 3️⃣ Solicitar una cotización 🧾 \n 4️⃣ Ver catálogo 📁 \n 5️⃣ Atención al Cliente🫡  \n 6️⃣ Horario de Atención🕙  \n 7️⃣ promociones disponibles 🔝 \n 8️⃣ Catalogo de jersey 100% sublimadas☑️ \n 9️⃣ Catalogo de franelas 100% sublimadas☑️ \n 1️⃣0️⃣ Catálogo de banderines 🏳️ \n 1️⃣1️⃣ Catálogo de lanyards🎗️"
            }
        }
        enviar_mensaje_separado(data)
    elif int(texto) == 1:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Para comprobar el estado de su pedido porfavor ingrese su número de cédula"
            }
        }
        enviar_mensaje_separado(data)
    elif "24694899" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Señor Ángel este es el estado de su pedido: \n ✅ Diseño \n ✅ Impresión \n ✅ sublimación \n ☑️ confección \n ☑️ entrega \n \n Se estima su pedido será terminado el 25-06-2024 \n \n Para volver al menú presione 0️⃣"
            }
        }
        enviar_mensaje_separado(data)
    elif "2" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "location": {
                "latitude": "7.770125285293934",
                "longitude": "-72.22545480674617",
                "name": "San Cristóbal tachira ",
                "address": "Poseidon Productos Corporativos"
            }
        }
        enviar_mensaje_separado(data)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "location": {
                "latitude": "10.247988913400468",
                "longitude": "-68.00714085026388",
                "name": "Valencia",
                "address": "Conjunto Residencial Las Quintas"
            }
        }
        enviar_mensaje_separado(data)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "location": {
                "latitude": "8.611486965609618",
                "longitude": "-70.23774073373085",
                "name": "Barinas",
                "address": "Zeus Productos Corporativos"
            }
        }
        enviar_mensaje_separado(data)
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "location",
            "location": {
                "latitude": "10.450597245285604",
                "longitude": "-66.91428893080374",
                "name": "Caracas",
                "address": "Autolavado Poseidon"
            }
        }
        enviar_mensaje_separado(data)
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "Pulsa 0️⃣ para regresar al menú."
            }
        }
        enviar_mensaje_separado(data)
        
    elif "3" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "3. Para solicitar una cotización llenar el siguiente formulario: \n - Nombre \n - ⁠cédula \n - ⁠teléfono \n- ⁠dirección \n \n Una vez estos datos sean suministrados se le asignará un número de pedido y será contactado por un asesor de ventas."
            }
        }
        enviar_mensaje_separado(data)
    elif "4" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "document",
            "document": {
                "link": "https://www.renfe.com/content/dam/renfe/es/General/PDF-y-otros/Ejemplo-de-descarga-pdf.pdf",
                "caption": "Catalogo General"
            }
        }
        enviar_mensaje_separado(data)
    elif "5" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": "atención al cliente lo mantiene"
            }
        }
        enviar_mensaje_separado(data)
    elif "6" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📅 Horario de Atención : Lunes a Viernes. \n🕜 Horario : 9:00 am a 5:00 pm 🤓"
            }
        }
        enviar_mensaje_separado(data)
    elif "7" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": True,
                "body": "Consulta todas nuestras ofertas en las historias del día de Instagram. \n https://www.instagram.com/poseidoncaracas?igsh=MWl1dnZhY3k3ZHR3NA=="
            }
        }
        enviar_mensaje_separado(data)
    elif "8" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": True,
                "body": "8. Catálogo de jersey: \n Mira esta artículo en WhatsApp: \n https://wa.me/p/7247225908697331/584143756059"
            }
        }
        enviar_mensaje_separado(data)
    elif "9" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": True,
                "body": "9. Catálogo de franelas: \n Mira esta artículo en WhatsApp: \n https://wa.me/p/24041477182162313/584143756059"
            }
        }
        enviar_mensaje_separado(data)
    elif "10" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": True,
                "body": "10. Catálogo de banderines: \n Mira esta artículo en WhatsApp: \n https://wa.me/p/5995984790529996/584143756059"
            }
        }
        enviar_mensaje_separado(data)
    elif "11" in texto:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": True,
                "body": "11. Catálogo de lanyard: \n Mira esta artículo en WhatsApp: \n https://wa.me/p/5537247556399218/584143756059"
            }
        }
        enviar_mensaje_separado(data)
    elif int(texto) > 11:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Las opciones que te ofrezco son un total de 11, consulta nuevamente cualquiera de las opciones asignadas."
            }
        }
    elif "0" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": numero,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "📌Por favor, ingresa un número #️⃣ para recibir información. \n 1️⃣ Información del pedido. ❔ \n 2️⃣ Ubicaciónes en el país📍 \n 3️⃣ Solicitar una cotización 🧾 \n 4️⃣ Ver catálogo 📁 \n 5️⃣ Atención al Cliente🫡  \n 6️⃣ Horario de Atención🕙  \n 7️⃣ promociones disponibles 🔝 \n 8️⃣ Catalogo de jersey 100% sublimadas☑️ \n 9️⃣ Catalogo de franelas 100% sublimadas☑️ \n 1️⃣0️⃣ Catálogo de banderines 🏳️ \n 1️⃣1️⃣ Catálogo de lanyards🎗️"
            }
        }
        enviar_mensaje_separado(data)
    
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "text": {
                "preview_url": False,
                "body": (
                    "No he comprendido tu mensaje, intentalo nuevamente."
                )
            }
        }
        enviar_mensaje_separado(data)
    

    
def enviar_mensaje_separado(data: dict):
    data = json.dumps(data)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAARqlwZAqLocBO58muUAQ5MS28LBYdPItxXlqJjP7IDeZBt2F5B8Bqeh0ZCAreKmWAm7Q2UDkme4uoZBwRgOBcHjacCbZApc5jwZAMUZAVGKHBCa26UeJJU9cWK0ZBzilE5JjH6fmQfQzZACi3JwrX02uLAnWOtqCHT3Uu9vh4IIZC20aYa6cXK5vhGICC5rh30wNcZCzZBZBGycTegVhYPKBY8wZD"
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