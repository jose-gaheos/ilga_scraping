#!/usr/bin/env python3
"""
Script de prueba para SearchPage (Supercias).
Ejecuta la página de búsqueda de manera standalone.
"""

import logging
from ghio_sri_bot_worker.sri_bot.core.browser_setup import BrowserSetup
from ghio_sri_bot_worker.sri_bot.config import const  # Asegúrate de que const tenga las constantes de Supercias
from ghio_sri_bot_worker.sri_bot.pages.supercias.search_page import SearchPage
from ghio_sri_bot_worker.sri_bot.ghsync_sri_v2 import GHSyncSRI_V2
import time
import os
from dotenv import load_dotenv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Carga las variables del archivo .env
load_dotenv()

api_key_2captcha = os.getenv('API_KEY_2CAPTCHA')
api_key_capsolver = os.getenv('API_KEY_CAPSOLVER')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_search.log', encoding='utf-8'),  # Guarda en archivo
        logging.StreamHandler(sys.stdout)  # También en consola
    ]
)
logger = logging.getLogger(__name__)


def main():
    # Configurar argumentos
    identification = "PICON BACULIMA LEONARDO MAURICIO"  # Cambia por una ID real para probar

    # Crear manager con GHSyncSupercias (maneja driver internamente)
    uid = "test_uid"
    manager = GHSyncSRI_V2(
        uid=uid,
        username="0921839023001",
        password="Armagedon@97",
        extra_ci="1791924037001",
        selenium_url='http://localhost:4444/wd/hub',  # Cambia si usas local
        solver_apikey=api_key_2captcha
    )

    try:
        # manager.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # Navegar a la URL del sitio
        # manager.driver.get("https://srienlinea.sri.gob.ec/sri-en-linea/contribuyente/perfil")
        manager.driver.get("https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc")
        # manager.driver.get("https://accounts.google.com/")
        print("Navegando a la URL del sitio...")
        
        # Instanciar y ejecutar SearchPage
        print("Ejecutando SearchPage...")
        result = manager.run()
        # result = page.run()
        print(f"Resultado de run(): {result}")

        if result:
            print("Búsqueda exitosa!")
        else:
            print("Búsqueda fallida. Revisa logs.")
            print(f"Estado final: {manager.state}, Acción: {manager.action}")

    except Exception as e:
        logger.error(f"Error ejecutando prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cerrando manager y driver...")
        manager.close()

if __name__ == '__main__':
    main()