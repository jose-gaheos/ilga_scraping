#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

from ..base_page import BasePage
from ...config import const
from selenium.webdriver.common.by import By
import requests
import base64
import re

class SearchPage(BasePage):
    def __init__(self, manager, identification, data, solver=None, extra_ci=None):
        super().__init__(manager)
        self._identification = identification
        self._extra_ci = extra_ci
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self._data = data
    

    def run(self):
        if not self.ensure_action(const.ACTION_LOGIN, const.STATE_INITIAL):
            print("Action or state not valid for SearchPage Juditial Function")
            return False

        self.action = const.ACTION_LOGIN, const.STATE_PENDING

        if input := self.wait_for_element_visible(const.JF_SELECTOR_INPUT, by=By.CSS_SELECTOR):
            self.move(input)
            self.send_keys(input, self._identification)
            self.wait(const.AWAIT_OPEN)
        else:
            self.state = const.STATE_ERROR
            return False

        if not self.is_safe:
            return False

        self.state = const.STATE_READY

        self.search_button_click()

        site_key = self.get_site_key()

        if not site_key:
            self.error("Site key not found")
            self.state = const.STATE_INVALID
            return False
        
        self.action = const.ACTION_RECAPTCHA, const.STATE_PENDING
        
        if not self.resolve_recaptcha(site_key=site_key):
            self.error("Recaptcha could not be resolved")
            self.state = const.STATE_ERROR
            return False
        
     

        
        if not self.ensure_action(const.ACTION_RECAPTCHA, const.STATE_SUCCESS):
            print("Action or state not valid before clicking search button")
            return False
        
        self.search_button_click()

        xpath_mensaje = "//div[contains(@class, 'mat-mdc-snack-bar-label') and contains(., 'La consulta no devolvió resultados')]"

        if self.wait_for_element_visible(xpath_mensaje, by=By.XPATH, timeout=const.TIMEOUT_MINIMUM):
            self.action = const.ACTION_HOME, const.STATE_INITIAL
            self.info("No se encontraron procesos judiciales")
            return True

        if self.wait_for_element_visible(const.JF_CLASS_LIST_CAUSES, by=By.CLASS_NAME, timeout=const.TIMEOUT_MINIMUM):
            self.action = const.ACTION_HOME, const.STATE_INITIAL
            self.info("Authentication successful")
            return True
        
       
    
        # try:
        #     elemento_mensaje = wait.until(EC.visibility_of_element_located((By.XPATH, xpath_mensaje)))
        #     print("¡Mensaje detectado!: " + elemento_mensaje.text)

        self.error("Authentication failed")
        self.state = const.STATE_FAILED
        return False
    
    def search_button_click(self):
        if button_search := self.wait_for_element(const.JF_SELECTOR_SEARCH_BUTTON, by=By.CSS_SELECTOR, timeout=const.TIMEOUT_MINIMUM):
            self.move(button_search)
            self.click(button_search)
        else:
            self.error('Search button not found')
            self.state = const.STATE_INVALID
            return False
    
    def get_site_key(self):
        try:
            iframe = self.wait_for_element(const.JF_XPATH_GET_SITE_KEY, by=By.XPATH, timeout=const.TIMEOUT_MINIMUM)
            src = iframe.get_attribute("src")

            # Buscamos lo que esté entre 'k=' y el siguiente '&'
            match = re.search(r'k=([^&]+)', src)
            
            if match:
                site_key = match.group(1)
                self.info(f"[+] Site Key encontrada: {site_key}")
                return site_key
            else:
                self.error("[-] No se encontró el parámetro 'k' en el iframe.")
                self.state = const.STATE_INVALID
                return None
        except Exception as e:
            self.error(f"[-] Error al extraer Site Key: {e}")
            self.state = const.STATE_ERROR
            return None
        
    def resolve_recaptcha(self, site_key):
        self.info("\n[!] Esperando resolución del captcha...")
        self.info(f"Current url for recaptcha: {self.driver.current_url}")
        response = self._solver.recaptcha(sitekey=site_key, url=self.driver.current_url)
        
        if token := response.get("code"):
            self.info(f"[+] Captcha resuelto manualmente: {token[:10]}") 
            self.driver.execute_script(self.get_script_inject_recapctha_token(token=token))
            self.action = const.ACTION_RECAPTCHA, const.STATE_SUCCESS
            return True
                
        return False
    
    def get_script_inject_recapctha_token(self, token):
        return f"""
                var token = '{token}';
                var cfg = window.___grecaptcha_cfg.clients[0];
                
                // 1. Buscamos dinámicamente el objeto que tiene el callback
                var encontrado = false;
                for (var i in cfg) {{
                    if (cfg[i] && cfg[i].F && cfg[i].F.callback) {{ // Basado en el hallazgo F.F
                        cfg[i].F.callback(token);
                        encontrado = true;
                        break;
                    }}
                    // Búsqueda genérica por si las letras cambian
                    for (var j in cfg[i]) {{
                        if (cfg[i][j] && cfg[i][j].callback) {{
                            cfg[i][j].callback(token);
                            encontrado = true;
                            break;
                        }}
                    }}
                    if (encontrado) break;
                }}
        """
    
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
            except Exception as e:
                print(f"No se pudo encontrar un elemento en el panel {index}")

            result_causas.append(data_item)

        return result_causas