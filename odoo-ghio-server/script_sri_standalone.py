#!/usr/bin/env python3
"""
Script standalone para ejecutar GHSyncSRI_V2 sin Odoo.
Extrae datos de RUC del SRI.
"""

import argparse
import logging
import os
from dotenv import load_dotenv

from ghio_sri_bot_worker.sri_bot.ghsync_sri_v2 import GHSyncSRI_V2

# Carga variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Bot SRI Standalone')
    parser.add_argument('--username', required=True, help='Usuario SRI')
    parser.add_argument('--password', required=True, help='Contraseña SRI')
    parser.add_argument('--extra_ci', required=True, help='CI adicional')
    parser.add_argument('--selenium_url', default='http://localhost:4444/wd/hub', help='URL Selenium')
    parser.add_argument('--home_path', default='/tmp/sri_standalone', help='Path base')
    parser.add_argument('--api_key', default=os.getenv('API_KEY_2CAPTCHA'), help='API Key 2Captcha')

    args = parser.parse_args()

    # Instancia el scraper
    scraper = GHSyncSRI_V2(
        uid='standalone_sri',
        username=args.username,
        password=args.password,
        extra_ci=args.extra_ci,
        selenium_url=args.selenium_url,
        home_path=args.home_path,
        solver_apikey=args.api_key
    )

    try:
        # Ejecuta el scraping
        success = scraper.run()
        if success:
            print("Scraping exitoso. Datos extraídos.")
            # Accede a scraper._data para los resultados
        else:
            print("Scraping fallido. Revisa logs.")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == '__main__':
    main()