from flask import Flask, request, jsonify
import threading
import requests
from tests.juditial_function import init_juditial_funciton_page

app = Flask(__name__)

# Configuración: URL del Webhook de Odoo
ODOO_WEBHOOK_URL = "https://tu-odoo-instancia.com/webscraping/callback"
WEBHOOK_SECRET = "mi_token_seguro_123"

status = (
    'draft',
    'in_process',
    'finished'
)

def exec_selenium_bot(identification, webhook_url):

    data_scraping = init_juditial_funciton_page(identification=identification)

    requests.post(webhook_url, json=data_scraping)


@app.route('/getInformation', methods=['POST'])
def init():
    data = request.json
    identification = data.get('identification')
    webhook_url = data.get('webhook_url')

    thread = threading.Thread(target=exec_selenium_bot, args=(identification, webhook_url))
    thread.start()
    
    return jsonify({"status": status[1], "mensaje": "La consulta ha iniciado"}), 202

if __name__ == "__main__":
    print("Ejecutando el servidor flask...")
    app.run(debug=True, port=5000)