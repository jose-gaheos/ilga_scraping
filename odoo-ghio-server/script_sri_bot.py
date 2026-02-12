#!/usr/bin/env python3
"""
Script standalone para ejecutar bots con Selenium.
Adaptado para integrar tu clase JuditialFunction.
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
from sri_bot.config import settings, const  # Asumiendo que const tiene tus constantes

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Aquí defines tus constantes si no están en sri_bot/config
# Ejemplo:
# JF_INPUT = (By.ID, "input_identification")
# JF_SEARCH_BUTTON = (By.CSS_SELECTOR, ".search-button")
# etc. Ajusta según tu config original.

# Simulación de scripts y recaptcha si no tienes módulos
class Scripts:
    @staticmethod
    def get_script_inject_recapctha_token(token):
        return f"""
        document.getElementById('g-recaptcha-response').innerHTML = '{token}';
        """

class SolveRecaptcha:
    @staticmethod
    def solve_recaptcha(site_key, page_url):
        # Aquí integra tu lógica de 2Captcha o manual
        # Ejemplo con 2Captcha
        solver = TwoCaptcha('TU_API_KEY')  # Reemplaza con tu key
        result = solver.recaptcha(sitekey=site_key, url=page_url)
        return result['code']


class JudicialFunction:
    def __init__(self, driver):
        self.driver = driver
        # Ajusta estas constantes según tu config
        self.input_text = const.JF_INPUT if hasattr(const, 'JF_INPUT') else (By.ID, "input_identification")
        self.button_search = const.JF_SEARCH_BUTTON if hasattr(const, 'JF_SEARCH_BUTTON') else (By.CSS_SELECTOR, ".search-button")

    def enter_identification(self, identification):
        element = self.driver.find_element(*self.input_text)
        element.clear()
        element.send_keys(identification)
        element.send_keys(Keys.TAB)

    def first_click_search_button(self):
        wait = WebDriverWait(self.driver, 5)
        try:
            button = wait.until(EC.element_to_be_clickable(self.button_search))
            button.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            button = wait.until(EC.presence_of_element_located(self.button_search))
            self.driver.execute_script("arguments[0].click();", button)

    def get_site_key(self):
        try:
            wait_iframe = WebDriverWait(self.driver, 10)
            xpath_iframe = const.JF_XPATH_GET_SITE_KEY if hasattr(const, 'JF_XPATH_GET_SITE_KEY') else "//iframe[contains(@src, 'recaptcha')]"
            iframe = wait_iframe.until(EC.presence_of_element_located((By.XPATH, xpath_iframe)))
            src = iframe.get_attribute("src")
            match = re.search(r'k=([^&]+)', src)
            if match:
                site_key = match.group(1)
                print(f"[+] Site Key encontrada: {site_key}")
                return site_key
            else:
                print("[-] No se encontró el parámetro 'k' en el iframe.")
                return None
        except Exception as e:
            print(f"[-] Error al extraer Site Key: {e}")
            return None

    def resolve_captcha_manual(self, site_key, page_url):
        print("\n[!] Esperando resolución del captcha...")
        token = SolveRecaptcha.solve_recaptcha(site_key=site_key, page_url=page_url)
        print(f"Token recaptcha {token[:30]}")
        self.driver.execute_script(Scripts.get_script_inject_recapctha_token(token))
        return token

    def get_data_causes(self):
        try:
            wait_explicit = WebDriverWait(self.driver, 10)
            results_url = const.JF_RESULTS if hasattr(const, 'JF_RESULTS') else "results"
            wait_explicit.until(EC.url_contains(results_url))
            print(f"URL detectada: {self.driver.current_url}")
            list_causes = self.driver.find_elements(By.CLASS_NAME, "causa-individual")
            print(f"Se encontraron {len(list_causes)} causas.")
            result_causes = self.get_list_causes(list_causes)
            return result_causes
        except Exception as e:
            print(f"Error tras el submit: {e}")

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
                print(f"No se pudo encontrar un elemento en el panel {index}")
        return result_causas


class JudicialBot:
    def __init__(self, selenium_url='http://localhost:4444/wd/hub', download_path='/tmp/downloads', profile_path='/tmp/profile'):
        self._selenium_url = selenium_url
        self._download_path = download_path
        self._profile_path = profile_path
        self._ensure_paths()
        self.driver = BrowserSetup(selenium_url, profile_path, download_path).setup()
        self.judicial = JudicialFunction(self.driver)

    def run_search(self, identification):
        """Ejecuta la búsqueda judicial."""
        try:
            self.judicial.enter_identification(identification)
            self.judicial.first_click_search_button()
            site_key = self.judicial.get_site_key()
            if site_key:
                page_url = self.driver.current_url
                self.judicial.resolve_captcha_manual(site_key, page_url)
                # Después de resolver captcha, hacer clic de nuevo o esperar
                time.sleep(2)  # Ajusta según necesites
                data = self.judicial.get_data_causes()
                return data
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
        finally:
            self.close()

    def close(self):
        if self.driver:
            self.driver.quit()

    def _ensure_paths(self):
        import os
        for path in [self._download_path, self._profile_path]:
            if not os.path.exists(path):
                os.makedirs(path)


def main():
    parser = argparse.ArgumentParser(description='Bot Judicial con Selenium')
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