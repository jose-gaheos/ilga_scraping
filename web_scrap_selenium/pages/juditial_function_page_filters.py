from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import re
import time
from config import const, scripts
from recaptcha import solve_recaptcha
#0919544171

class JuditialFunction:
    def __init__(self, driver):
        self.driver = driver

        self.input_text = const.JF_INPUT
        self.button_search = const.JF_SEARCH_BUTTON #opcion con selector css

    def enter_identification(self, identification):
        element = self.driver.find_element(*self.input_text)
        element.clear()
        element.send_keys(identification)
        element.send_keys(Keys.TAB)

    def first_click_search_button(self):
        wait = WebDriverWait(self.driver, 5)
        try:
            # Esperamos a que sea clicable (que no esté disabled)
            button = wait.until(EC.element_to_be_clickable(self.button_search))
            button.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            # Si el botón se "refrescó" justo al clicar, lo buscamos de nuevo y usamos JS
            button = wait.until(EC.presence_of_element_located(self.button_search))
            self.driver.execute_script("arguments[0].click();", button)

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

            # accordion = wait_explicit.until(EC.visibility_of_element_located(const.JF_ACCORDION_CAUSES))

            list_causes =  self.driver.find_elements(By.CLASS_NAME, "causa-individual")
            # list_causes = accordion.find_elements(By.TAG_NAME, const.JF_PANELES_NAME)
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
            except Exception as e:
                print(f"No se pudo encontrar un elemento en el panel {index}")

            result_causas.append(data_item)

        return result_causas

    
   



