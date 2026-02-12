from selenium import webdriver
import os
import time
import undetected_chromedriver as uc
import json
# 1. Obtener la ruta raíz de tu proyecto (donde está este archivo)
# Si este script está en /pages/supercias_page.py, subimos niveles:
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Definir la carpeta de descargas dentro de tu proyecto
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

# 3. Crear la carpeta si no existe para evitar errores
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Configuración para guardado automático de PDF
settings = {
    "recentDestinations": [{
        "id": "Save as PDF",
        "origin": "local",
        "account": ""
    }],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}

prefs = {
    "download.default_directory": DOWNLOAD_DIR, # Cambia esto
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True, # Forzar descarga
    "download.directory_upgrade": True,
    "printing.print_preview_sticky_settings.appState": json.dumps(settings),
    "savefile.default_directory": DOWNLOAD_DIR
}

def get_default_chrome_options():
    options = uc.ChromeOptions()

    # options.add_argument('--headless=new')

    # Configuraciones necesarias para evitar detección y errores de renderizado
    # options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080') # Tamaño de pantalla virtual
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

   # Esta es la clave para quitar el banner en versiones recientes
    options.add_argument('--disable-blink-features=AutomationControlled')

    options.add_experimental_option('prefs', prefs)
    options.add_argument('--kiosk-printing') # Esta es la clave: imprime sin ventana emergente

    # Evita que se activen las extensiones de automatización de Chrome
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    # options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    return options

def wait_for_download(directory, timeout=30):
    seconds = 0
    while seconds < timeout:
        # Busca archivos que terminen en .pdf (o .crdownload mientras baja)
        files = os.listdir(directory)
        if any(f.endswith(".pdf") for f in files):
            return True
        time.sleep(1)
        seconds += 1
    return False