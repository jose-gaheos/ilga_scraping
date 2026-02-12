#!/usr/bin/env python3
"""
Script de prueba para SearchPage (Supercias).
Ejecuta la página de búsqueda de manera standalone.
"""

import logging
from ghio_sri_bot_worker.sri_bot.core.browser_setup import BrowserSetup
from ghio_sri_bot_worker.sri_bot.config import const  # Asegúrate de que const tenga las constantes de Supercias
from ghio_sri_bot_worker.sri_bot.pages.supercias.search_page import SearchPage
from ghio_sri_bot_worker.sri_bot.ghsync_supercias import GHSyncSupercias
import time
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

api_key_2captcha = os.getenv('API_KEY_2CAPTCHA')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_PATH_FILES = os.path.join(BASE_DIR, "supercias_files")

if not os.path.exists(HOME_PATH_FILES):
    os.makedirs(HOME_PATH_FILES)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_search.log'),  # Guarda en archivo
        logging.StreamHandler()  # También en consola
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Configurar argumentos
    identification = "0993236497001"  # Cambia por una ID real para probar

    # Crear manager con GHSyncSupercias (maneja driver internamente)
    uid = "supercias_uid"
    manager = GHSyncSupercias(
        uid=uid,
        identification=identification,
        selenium_url='http://localhost:4444/wd/hub',  # Cambia si usas local
        solver_apikey=api_key_2captcha,
        home_path='/tmp/files'
    )

    try:
        # Navegar a la URL del sitio
        manager.driver.get("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf")
        # print("Navegando a la URL del sitio...")
        
        # Instanciar y ejecutar SearchPage
        # page = SearchPage(manager, identification=identification)
        # print("Ejecutando SearchPage...")
        result = manager.run()
        # result = page.run()
        # print(f"Resultado de run(): {result}")

        if result:
            print(f'STATE = "{manager.state}"')
            print(f'ACTION = "{manager.action}"')
            print("Búsqueda exitosa!")
        else:
            print("Búsqueda fallida. Revisa logs.")
            # print(f"Estado final: {manager.state}, Acción: {manager.action}")

    except Exception as e:
        logger.error(f"Error ejecutando prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.close()

if __name__ == '__main__':
    main()