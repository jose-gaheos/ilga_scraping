#!/usr/bin/env python3
"""
Script standalone para ejecutar DocumentsPage sin Odoo.
Descarga documentos del SRI.
"""

import argparse
import logging
import os
import datetime
from dotenv import load_dotenv

from ghio_sri_bot_worker.sri_bot.ghsync_sri import GHSyncSRI
from ghio_sri_bot_worker.sri_bot.pages.documents_page import DocumentsPage

# Carga variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='DocumentsPage Standalone')
    parser.add_argument('--username', required=True, help='Usuario SRI')
    parser.add_argument('--password', required=True, help='Contraseña SRI')
    parser.add_argument('--extra_ci', required=True, help='CI adicional')
    parser.add_argument('--selenium_url', default='http://localhost:4444/wd/hub', help='URL Selenium')
    parser.add_argument('--home_path', default='/tmp/sri_docs', help='Path base')
    parser.add_argument('--api_key', default=os.getenv('API_KEY_2CAPTCHA'), help='API Key 2Captcha')
    parser.add_argument('--year', type=int, default=2023, help='Año')
    parser.add_argument('--month', type=int, default=10, help='Mes')
    parser.add_argument('--document_type', default='01', help='Tipo de documento')

    args = parser.parse_args()

    # Instancia el scraper para login
    scraper = GHSyncSRI(
        uid='docs_standalone',
        username=args.username,
        password=args.password,
        extra_ci=args.extra_ci,
        selenium_url=args.selenium_url,
        home_path=args.home_path,
        solver_apikey=args.api_key
    )

    try:
        # Login
        if not scraper.run_auth():
            print("Login failed")
            return

        # Define tasks (puedes agregar más)
        tasks = [{
            'year': args.year,
            'month': args.month,
            'day': 1,  # Día arbitrario
            'document_type': args.document_type,
            'date_from': datetime.date(args.year, args.month, 1),
            'date_to': datetime.date(args.year, args.month, 28)  # Ajusta según mes
        }]

        # Instancia DocumentsPage con tasks
        docs_page = DocumentsPage(
            manager=scraper,
            tasks=tasks,
            solver=scraper.solver,
            download_base_path=os.path.join(args.home_path, 'downloads')
        )

        # Ejecuta descarga
        success = docs_page.run()
        if success:
            print("Document download completed successfully.")
        else:
            print("Document download failed.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == '__main__':
    main()