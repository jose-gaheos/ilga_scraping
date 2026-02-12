import threading
import subprocess
import requests
from flask import Flask, jsonify, request, send_from_directory
from concurrent.futures import ThreadPoolExecutor

from ghio_sri_bot_worker.sri_bot.ghsync_supercias import GHSyncSupercias
from ghio_sri_bot_worker.sri_bot.ghsync_juditial import GHSyncJuditial
from ghio_sri_bot_worker.sri_bot.ghsync_sri_v2 import GHSyncSRI_V2

import os
import json

from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

LOCAL_FILES_DIR = os.getenv('PATH_FILES')

app = Flask(__name__)

def worker_scraper(ClaseScraper, identification, id_consulta, nombre, username_sri, password_sri):
    """
    Función que ejecuta la lógica de la clase y retorna el resultado estructurado
    """
    # Configuramos una ruta única para los PDF de esta consulta
    path_archivos = f"/tmp/files"
    print("identification es: ", identification)
    print("Nombre es: ", nombre)

    extra_ci = identification
    # Instanciamos el manager (usando tu lógica actual)
    manager = ClaseScraper(
        uid=id_consulta,
        identification= extra_ci,
        username=username_sri,
        password = password_sri,
        nombre = nombre,
        extra_ci = extra_ci,
        selenium_url='http://localhost:4444/wd/hub',
        solver_apikey=os.getenv('API_KEY_2CAPTCHA'),
        home_path=path_archivos
    )

    try:
        # Navegación inicial (como hacías en el main)
        # url_sitio = "URL_ESPECIFICA_DE_CADA_CLASE" # Podrías tener esto como atributo de clase
        # manager.driver.get(url_sitio)
        
        # Ejecución
        exito = manager.run()
        data = getattr(manager, '_data', {})
        
        response = {
            "scraper": ClaseScraper.__name__,
            "exito": exito,
            "state": manager.state,
            "action": manager.action,
            "archivos_path": path_archivos,
            "data": data
        }
        return response
    except Exception as e:
        return {"scraper": ClaseScraper.__name__, "exito": False, "error": str(e)}
    finally:
        manager.close() # Importante para liberar el nodo en Docker

def orquestar_y_notificar(lista_clases, identification, webhook_url, id_consulta, nombre, username_sri, password_sri):
    # Ejecutamos en paralelo (ThreadPoolExecutor es ideal para Selenium)
    with ThreadPoolExecutor(max_workers=len(lista_clases)) as executor:
        futuros = [
            executor.submit(worker_scraper, cls, identification, id_consulta, nombre, username_sri, password_sri) 
            for cls in lista_clases
        ]
        resultados = [f.result() for f in futuros]

    # Webhook final con todos los objetos de respuesta
    payload = {
        "id_consulta": id_consulta,
        "identificacion": identification,
        "status_general": "COMPLETADO",
        "resultados": resultados
    }

    print("Enviando payload al webhook:", json.dumps(payload, indent=4))
    
    requests.post(webhook_url, json=payload, timeout=15)


@app.route('/tmp/files/<path:path_file>')
def serve_scraping_file(path_file):
    # LOCAL_FILES_DIR = "/Users/josecruz/Documents/SeleniumProjects/odoo-ghio-server/files"
    
    # 1. Verificar si el archivo existe para debuggear (puedes quitarlo luego)
    file_path = os.path.join(f"{LOCAL_FILES_DIR}", path_file)
    print(f"Buscando archivo en: {file_path}")
    
    if not os.path.exists(file_path):
        return f"Archivo no encontrado en el sistema: {file_path}", 404

    # 2. Servir el archivo
    return send_from_directory(LOCAL_FILES_DIR, path_file)


@app.route('/api/v1/consultar', methods=['POST'])
def endpoint_consultar():
    data = request.json
    identificacion = data.get("identificacion")
    id_consulta = data.get("id_consulta")
    webhook = data.get("webhook_url")
    nombre = data.get("nombre")
    username_sri = data.get("username_sri")
    password_sri = data.get("password_sri")
    # Lista de tus clases de manager
    clases_a_ejecutar = [ GHSyncSRI_V2]
    # clases_a_ejecutar = [GHSyncSRI_V2]

    # Disparar hilo principal para no bloquear la respuesta HTTP
    threading.Thread(
        target=orquestar_y_notificar, 
        args=(clases_a_ejecutar, identificacion, webhook, id_consulta, nombre, username_sri, password_sri)
    ).start()

    return jsonify({
        "mensaje": "Consulta iniciada",
        "id_seguimiento": id_consulta
    }), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)