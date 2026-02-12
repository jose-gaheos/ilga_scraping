from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from config import const, scripts
from recaptcha import solve_recaptcha
#0919544171

class JuditialFunction:
    def __init__(self, driver):
        self.driver = driver

        self.input_identification = const.JF_INPUT
        self.button_search = const.JF_SEARCH_BUTTON #opcion con selector css

    def enter_identification(self, identification):
        element = self.driver.find_element(*self.input_identification)
        element.clear()
        element.send_keys(identification)

    def first_click_search_button(self):
        wait_explicit = WebDriverWait(self.driver, 100)
        button = wait_explicit.until(EC.element_to_be_clickable(self.button_search))
        button.click()
    
    def get_site_key(self):
        try:
            wait_iframe = WebDriverWait(self.driver, 10)
            xpath_iframe = const.JF_XPATH_GET_SITE_KEY
            # 1. Localizar el iframe de Google reCAPTCHA
            iframe = wait_iframe.until(EC.presence_of_element_located((By.XPATH, xpath_iframe)))
            # 2. Obtener el atributo 'src' que contiene la llave
            src = iframe.get_attribute("src")
            
            # 3. Usar una expresión regular para extraer el valor de 'k'
            # Buscamos lo que esté entre 'k=' y el siguiente '&'
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
    #search-form captcha
    def resolve_captcha_manual(self, site_key, page_url):
        print("\n[!] Esperando resolución del captcha...")
        token = solve_recaptcha.solve_recaptcha(site_key=site_key, page_url=page_url)
        print(f"Token recaptcha {token[:30]}")
       
        self.driver.execute_script(scripts.get_script_inject_recapctha_token(token))
                
        return token
    
    def get_data_causes(self):
        try:
            wait_explicit = WebDriverWait(self.driver, 10)
            wait_explicit.until(EC.url_contains(const.JF_RESULTS)) 

            print(f"URL detectada: {self.driver.current_url}")

            accordion = wait_explicit.until(EC.visibility_of_element_located(const.JF_ACCORDION_CAUSES))

            paneles = accordion.find_elements(By.TAG_NAME, const.JF_PANELES_NAME)
            print(f"Se encontraron {len(paneles)} causas.")

            lista_causas = self.get_list_causes_from_paneles(paneles)

            return lista_causas


        except Exception as e:
            print(f"Error tras el submit: {e}")

    
    def get_list_causes_from_paneles(self, paneles):
        lista_causas = []
        for index, panel in enumerate(paneles):
            try:
                header = panel.find_element(By.TAG_NAME, const.JF_PANEL_HEADER)
                header_text = header.find_element(By.XPATH, const.JF_TITLE_CAUSE).text
                header_code = header.find_element(By.XPATH, const.JF_CODE_CAUSE).text

                data_item = {
                    "index": index,
                    "title": header_text,
                    "code": header_code,
                    "detalles": {}
                }
            except Exception as e:
                print(f"No se pudo encontrar un elemento en el panel {index}")

            lista_causas.append(data_item)

        return lista_causas

    
   



