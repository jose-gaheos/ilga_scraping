import threading
import subprocess
import requests
import os
import json
from flask import Flask, jsonify, request, send_from_directory
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Importación de tus clases de scraping
from ghio_sri_bot_worker.sri_bot.ghsync_supercias import GHSyncSupercias
from ghio_sri_bot_worker.sri_bot.ghsync_juditial import GHSyncJuditial
from ghio_sri_bot_worker.sri_bot.ghsync_sri_v2 import GHSyncSRI_V2

# Carga las variables del archivo .env
load_dotenv()

LOCAL_FILES_DIR = os.getenv('PATH_FILES')
app = Flask(__name__)

# --- LÓGICA DEL WORKER ---

def worker_scraper(config):
    """
    Función que recibe un diccionario con la clase y sus parámetros específicos.
    """
    ClaseScraper = config['class']
    params = config['params']
    
    # Parámetros técnicos comunes (no necesitan venir del request de usuario)
    params.update({
        "solver_apikey": os.getenv('API_KEY_2CAPTCHA'),
        "home_path": "/tmp/files"
    })

    print(f"Iniciando {ClaseScraper.__name__} para: {params.get('identification')}")

    # Instanciamos dinámicamente usando desempaquetado de diccionarios (**)
    manager = ClaseScraper(**params)

    try:
        exito = manager.run()
        # Intentamos obtener los datos si el scraper los generó
        data = getattr(manager, '_data', {})
        
        return {
            "scraper": ClaseScraper.__name__,
            "exito": exito,
            "state": getattr(manager, 'state', 'N/A'),
            "action": getattr(manager, 'action', 'N/A'),
            "data": data
        }
    except Exception as e:
        print(f"Error en {ClaseScraper.__name__}: {str(e)}")
        return {
            "scraper": ClaseScraper.__name__, 
            "exito": False, 
            "error": str(e)
        }
    finally:
        # Liberar recursos de Selenium/Docker
        if hasattr(manager, 'close'):
            manager.close()

# --- ORQUESTADOR ---

def orquestar_y_notificar(configuraciones, webhook_url, id_consulta, identificacion):
    """
    Ejecuta los scrapers en paralelo y envía el resultado al webhook.
    """
    
    
    with ThreadPoolExecutor(max_workers=len(configuraciones)) as executor:
        # Mapeamos cada configuración a un hilo
        futuros = [executor.submit(worker_scraper, conf) for conf in configuraciones]
        resultados = [f.result() for f in futuros]

    # Payload consolidado para el Webhook
    payload = {
        "id_consulta": id_consulta,
        "identificacion": identificacion,
        "status_general": "COMPLETADO",
        "resultados": resultados
    }

    print(f"Enviando resultados al webhook: {webhook_url}")
    try:
        requests.post(webhook_url, json=payload, timeout=20)
    except Exception as e:
        print(f"Error enviando el webhook: {e}")

# --- RUTAS FLASK ---

@app.route('/tmp/files/<path:path_file>')
def serve_scraping_file(path_file):
    file_path = os.path.join(str(LOCAL_FILES_DIR), path_file)
    if not os.path.exists(file_path):
        return f"Archivo no encontrado: {file_path}", 404
    return send_from_directory(LOCAL_FILES_DIR, path_file)

@app.route('/api/v1/consultar', methods=['POST'])
def endpoint_consultar():
    data = request.json
    
    # Extraemos datos del body
    identificacion = data.get("identificacion")
    id_consulta = data.get("id_consulta")
    webhook = data.get("webhook_url")
    nombre = data.get("nombre")
    # user_sri = data.get("username_sri")
    # pass_sri = data.get("password_sri")

    # --- DEFINICIÓN DE CONFIGURACIONES ESPECÍFICAS ---
    # Aquí es donde instancias cada uno con sus propios parámetros
    configuraciones = [
        {
            "class": GHSyncSupercias,
            "params": {
                "uid": id_consulta,
                "identification": identificacion,
                "nombre": nombre,
                "extra_ci": identificacion,
                "selenium_url": f'http://localhost:4445/wd/hub',
            }
        },
        {
            "class": GHSyncSRI_V2,
            "params": {
                "uid": id_consulta,
                "identification": identificacion,
                "nombre": nombre,
                "extra_ci": identificacion,
                "selenium_url": f'http://localhost:4444/wd/hub',
            }
        },
        {
            "class": GHSyncJuditial,
            "params": {
                "uid": id_consulta,
                "identification": identificacion,
                "nombre": nombre,
                "extra_ci": identificacion,
                "selenium_url": f'http://localhost:4446/wd/hub',
            }
        },
        # Puedes agregar GHSyncJuditial aquí si lo necesitas
    ]

    # Disparar el hilo principal para no bloquear la respuesta HTTP 202
    threading.Thread(
        target=orquestar_y_notificar, 
        args=(configuraciones, webhook, id_consulta, identificacion)
    ).start()

    return jsonify({
        "mensaje": "Proceso de scraping iniciado en segundo plano",
        "id_seguimiento": id_consulta
    }), 202

if __name__ == '__main__':
    # Nota: debug=True en hilos puede causar ejecuciones dobles, 
    # en producción usar False.
    app.run(host='0.0.0.0', port=5001, debug=True)