#!/usr/bin/env python3
"""
Script standalone para ejecutar bots con Selenium.
Tu clase JudicialFunction adaptada como página, similar a login_page.py (Page Object Model).
"""

import datetime
import time
import argparse
import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from twocaptcha import TwoCaptcha

from sri_bot.core.browser_setup import BrowserSetup
from sri_bot.config import settings, const
from sri_bot.core.ghsync_base import GHSyncBase  # Para BasePage

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simulación de scripts y recaptcha
class Scripts:
    @staticmethod
    def get_script_inject_recapctha_token(token):
        return f"""
        document.getElementById('g-recaptcha-response').innerHTML = '{token}';
        """

class SolveRecaptcha:
    @staticmethod
    def solve_recaptcha(site_key, page_url):
        solver = TwoCaptcha('TU_API_KEY')  # Reemplaza con tu key
        result = solver.recaptcha(sitekey=site_key, url=page_url)
        return result['code']


class BasePage(GHSyncBase):
    """BasePage adaptada para standalone."""
    @property
    def driver(self):
        return self.manager.driver

    @property
    def driver_actions(self):
        return self.manager.driver_actions

    def wait_for_element(self, selector, by=By.XPATH, timeout=10, mute=False):
        if not mute:
            self.info(f"Waiting for element: {selector}")
        element = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        if not mute:
            self.info(f"Element found: {selector}")
        return element

    def click(self, element, wait=1):
        element.click()
        if wait:
            time.sleep(wait)

    def send_keys(self, element, keys, wait=1):
        element.send_keys(keys)
        if wait:
            time.sleep(wait)

    def execute_script(self, script):
        return self.driver.execute_script(script)


class JudicialPage(BasePage):
    """Tu clase JudicialFunction adaptada como página, similar a login_page.py."""
    
    def __init__(self, manager, identification):
        super().__init__(manager)
        self.identification = identification
        # Constantes (ajusta según tu config)
        self.input_text = const.JF_INPUT if hasattr(const, 'JF_INPUT') else (By.ID, "input_identification")
        self.button_search = const.JF_SEARCH_BUTTON if hasattr(const, 'JF_SEARCH_BUTTON') else (By.CSS_SELECTOR, ".search-button")

    def run(self):
        """Método run() similar a login_page.py, ejecuta el flujo completo."""
        self.action = "SEARCH", "PENDING"
        
        # Paso 1: Ingresar identificación
        if not self.enter_identification():
            self.state = "ERROR"
            return False
        
        # Paso 2: Hacer clic en buscar
        if not self.click_search_button():
            self.state = "ERROR"
            return False
        
        # Paso 3: Resolver captcha
        site_key = self.get_site_key()
        if site_key:
            page_url = self.driver.current_url
            if not self.resolve_captcha(site_key, page_url):
                self.state = "ERROR"
                return False
        
        # Paso 4: Obtener datos
        data = self.get_data_causes()
        if data is None:
            self.state = "ERROR"
            return False
        
        self.state = "SUCCESS"
        self.info("Búsqueda judicial completada")
        return data

    def enter_identification(self):
        try:
            element = self.wait_for_element(self.input_text[1], by=self.input_text[0])
            element.clear()
            self.send_keys(element, self.identification)
            element.send_keys(Keys.TAB)
            return True
        except Exception as e:
            self.error(f"Error al ingresar identificación: {e}")
            return False

    def click_search_button(self):
        try:
            button = self.wait_for_element(self.button_search[1], by=self.button_search[0])
            self.click(button)
            return True
        except (StaleElementReferenceException, ElementClickInterceptedException) as e:
            try:
                button = self.wait_for_element(self.button_search[1], by=self.button_search[0])
                self.execute_script("arguments[0].click();", button)
                return True
            except Exception as e2:
                self.error(f"Error al hacer clic en buscar: {e2}")
                return False

    def get_site_key(self):
        try:
            xpath_iframe = const.JF_XPATH_GET_SITE_KEY if hasattr(const, 'JF_XPATH_GET_SITE_KEY') else "//iframe[contains(@src, 'recaptcha')]"
            iframe = self.wait_for_element(xpath_iframe)
            src = iframe.get_attribute("src")
            match = re.search(r'k=([^&]+)', src)
            if match:
                site_key = match.group(1)
                self.info(f"Site Key encontrada: {site_key}")
                return site_key
            else:
                self.warn("No se encontró el parámetro 'k' en el iframe.")
                return None
        except Exception as e:
            self.error(f"Error al extraer Site Key: {e}")
            return None

    def resolve_captcha(self, site_key, page_url):
        try:
            self.info("Resolviendo captcha...")
            token = SolveRecaptcha.solve_recaptcha(site_key=site_key, page_url=page_url)
            self.execute_script(Scripts.get_script_inject_recapctha_token(token))
            return True
        except Exception as e:
            self.error(f"Error resolviendo captcha: {e}")
            return False

    def get_data_causes(self):
        try:
            results_url = const.JF_RESULTS if hasattr(const, 'JF_RESULTS') else "results"
            WebDriverWait(self.driver, 10).until(EC.url_contains(results_url))
            self.info(f"URL detectada: {self.driver.current_url}")
            list_causes = self.driver.find_elements(By.CLASS_NAME, "causa-individual")
            self.info(f"Se encontraron {len(list_causes)} causas.")
            return self.get_list_causes(list_causes)
        except Exception as e:
            self.error(f"Error obteniendo datos: {e}")
            return None

    def get_list_causes(self, list_causes):
        result_causas = []
        for index, causa in enumerate(list_causes):
            try:
                cause_id = causa.find_element(By.CLASS_NAME, "id").text
                process_number = causa.find_element(By.CLASS_NAME, "fecha").text
                process_date = causa.find_element(By.CLASS_NAME, "numero-proceso").text
                action = causa.find_element(By.CLASS_NAME, "accion-infraccion").text
                data_item = {
                    "id": cause_id,
                    "number": process_number,
                    "date": process_date,
                    "action": action
                }
                result_causas.append(data_item)
            except Exception as e:
                self.warn(f"No se pudo encontrar un elemento en el panel {index}: {e}")
        return result_causas


class JudicialBot:
    def __init__(self, selenium_url='http://localhost:4444/wd/hub', download_path='/tmp/downloads', profile_path='/tmp/profile'):
        self._selenium_url = selenium_url
        self._download_path = download_path
        self._profile_path = profile_path
        self._ensure_paths()
        self.driver = BrowserSetup(selenium_url, profile_path, download_path).setup()
        # Agregar propiedades para que actúe como manager
        self.state = "INITIAL"
        self.action = "SETTINGS"
        self.logger = logger

    def run_search(self, identification):
        """Ejecuta la búsqueda usando JudicialPage."""
        page = JudicialPage(self, identification)
        return page.run()

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)
        return False

    def warn(self, message):
        self.logger.warning(message)
        return True

    def close(self):
        if self.driver:
            self.driver.quit()

    def _ensure_paths(self):
        import os
        for path in [self._download_path, self._profile_path]:
            if not os.path.exists(path):
                os.makedirs(path)


def main():
    parser = argparse.ArgumentParser(description='Bot Judicial con Selenium (Page Object Model)')
    parser.add_argument('--identification', required=True, help='Identificación a buscar')
    parser.add_argument('--selenium-url', default='http://localhost:4444/wd/hub', help='URL de Selenium')
    parser.add_argument('--download-path', default='/tmp/judicial_downloads', help='Path de descargas')
    parser.add_argument('--profile-path', default='/tmp/judicial_profile', help='Path del perfil')

    args = parser.parse_args()

    bot = JudicialBot(
        selenium_url=args.selenium_url,
        download_path=args.download_path,
        profile_path=args.profile_path
    )

    try:
        data = bot.run_search(args.identification)
        if data:
            print("Datos obtenidos:", data)
        else:
            print("No se obtuvieron datos.")
    except Exception as e:
        logger.error(f"Error ejecutando el bot: {e}")
    finally:
        bot.close()


if __name__ == '__main__':
    main()