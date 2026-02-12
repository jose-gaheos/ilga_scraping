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
from ...utils.functions import escribir_con_error_humano
import time
import capsolver
import os
import json

from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

capsolver.api_key = os.getenv('API_KEY_CAPSOLVER')

class RucPage(BasePage):
    def __init__(self, manager, data, extra_ci=None, solver=None):
        super().__init__(manager)
        self._extra_ci = extra_ci
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self._data = data
    

    def run(self):
        # self.inyectar_scripts_antideteteccion()
        if not self.ensure_action(const.ACTION_HOME, const.STATE_INITIAL):
            print("Action or state not valid for SearchPage Juditial Function")
            return False

        self.action = const.ACTION_HOME, const.STATE_PENDING
        self.wait(const.AWAIT_OPEN)
        if button_menu_ruc := self.wait_for_element(const.SRI_ID_BUTTON_MENU, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            self.move(button_menu_ruc)
            self.click(button_menu_ruc)
        else:
            self.error('Button menu not found')
            self.state = const.STATE_INVALID
            return False
        
        self.wait(const.AWAIT_OPEN)
        if menu_ruc := self.wait_for_element(const.SRI_XPATH_MENU_ITEM_RUC, timeout=const.TIMEOUT_MINIMUM):
            self.move(menu_ruc)
            self.click(menu_ruc)
        else:
            self.error('RUC menu item not found')
            self.state = const.STATE_INVALID
            return False
        
        self.wait(const.AWAIT_OPEN)

        if item_ruc := self.wait_for_element_clickable(const.SRI_XPATH_MENU_ITEM_CONSULTA, timeout=const.TIMEOUT_MINIMUM):
            self.move(item_ruc)
            self.click(item_ruc)
            self.wait(const.AWAIT_OPEN)
            self.state = const.STATE_READY
        else:
            self.error('RUC consultation item not found')
            self.state = const.STATE_INVALID
            return False
        
        self.wait(const.AWAIT_OPEN)

        if input_ruc := self.find_element(const.SRI_ID_INPUT_SEARCH, by=By.ID):
            self.move(input_ruc)
            self.wait(const.AWAIT_OPEN)
            self.click(input_ruc)
            if self._extra_ci:
                self.send_keys(input_ruc, self._extra_ci)
                # escribir_con_error_humano(elemento= input_ruc, texto = self._extra_ci, error_delete=-2)
            else:
                self.info(f"No extra CI provided for RUC search: {self._extra_ci}")
                self.state = const.STATE_INVALID
                return False
        else:
            self.error('RUC input field not found')
            self.state = const.STATE_INVALID
            return False
        
        # site_key = self.get_site_key()

        # if not site_key:
        #     self.error("Site key not found")
        #     self.state = const.STATE_INVALID
        #     return False
        
        # self.action = const.ACTION_RECAPTCHA, const.STATE_PENDING
        
        # if not self.resolve_recaptcha_v3(site_key=site_key):
        #     self.error("Recaptcha could not be resolved")
        #     self.state = const.STATE_ERROR
        #     return False
        
        # if not self.ensure_action(const.ACTION_RECAPTCHA, const.STATE_SUCCESS):
        #     print("Action or state not valid before clicking search button")
        #     return False
        
        # if self.consultar_con_solver():
        #     self.info("RUC data retrieved successfully")
        #     self.state = const.STATE_SUCCESS
        #     # Aquí puedes agregar la lógica para extraer y almacenar los datos del RUC
        #     return True

        if not self.consultar_con_reintento(max_intentos=5):
            self.info("RUC data retrieved error after retries")
            self.state = const.STATE_ERROR
            return False
        

        self.info("RUC data retrieved successfully")
        self.state = const.STATE_READY

        if self.extraer_datos_sri() and self.ensure_action(const.ACTION_HOME, const.STATE_SUCCESS):
            self.info("RUC data extraction completed successfully")
            return True
        
        # if button_search := self.wait_for_element_clickable(const.SRI_XPATH_BUTTON_SEARCH):
        #     self.move(button_search)
        #     self.click(button_search)
        #     self.wait(const.AWAIT_OPEN)
        # else:
        #     self.error('Search button not found')
        #     self.state = const.STATE_INVALID
        #     return False
        
        # if button_results := self.wait_for_element(const.SRI_XPATH_MORE_STABLISHMENTS, timeout=const.TIMEOUT_MINIMUM):
        #     self.move(button_results)
        #     self.click(button_results)
        #     self.wait(const.AWAIT_OPEN)
        #     self.state = const.STATE_SUCCESS
        #     self.info("RUC data retrieved successfully")
        # else:
        #     self.error('More establishments button not found')
        #     self.state = const.STATE_INVALID
        #     return False

        self.error("Ruc page error")
        self.state = const.STATE_FAILED
        return False
    
    def extraer_datos_sri(self):
        datos = {}
        
        # 1. Extraer datos que vienen en formato Etiqueta -> Valor (divs)
        # Buscamos todos los elementos con la clase que el SRI usa para los títulos
        try: 
            # 2. Obtener el RUC y la Razón Social usando su clase de valor
            # Buscamos todos los elementos que tienen el valor real
            valores = self.find_elements(const.SRI_CLASS_ALL_VALUES, by=By.CLASS_NAME)
            
            # En el HTML del SRI:
            # El primer 'tamano-defecto-campos' suele ser el RUC
            # El segundo suele ser la Razón Social
            ruc = valores[0].text.strip() if len(valores) > 0 else None
            razon_social = valores[1].text.strip() if len(valores) > 1 else None

            datos["RUC"] = ruc
            datos["Razón Social"] = razon_social

            try:
                # 1. Localizamos el encabezado y Navegamos hacia el valor. 
                # En el HTML del SRI, el valor suele estar en el siguiente div con clase col-sm-6
                actividad_principal = self.find_element(const.SRI_XPATH_ACTIVITY_MAIN).text.strip()
                datos["actividad_economica"] = actividad_principal
            except:
                datos["actividad_economica"] = None

            titulos = self.find_elements(const.SRI_CLASS_LABEL_BOLD, by=By.CLASS_NAME)
        
            for titulo_el in titulos:
                titulo = titulo_el.text.strip().replace(":", "")
                if not titulo:
                    continue
                    
                try:
                    # El valor suele estar en el siguiente div hermano o en un span cercano
                    # Usamos una ruta relativa desde el título
                    valor = self.find_element(const.SRI_XPATH_DIV_VALUE, parent=titulo_el).text.strip()
                    # Limpieza para el caso del Representante Legal que tiene sub-campos
                    if "Nombre/Razón Social" in titulo:
                        # Caso específico para la estructura anidada del representante
                        datos["Representante_Nombre"] = self.find_element(const.SRI_XPATH_LEGAL_NAME, parent=titulo_el).text.strip()
                    elif "Identificación" in titulo:
                        datos["Representante_ID"] = self.find_element("./following-sibling::div[1]", parent=titulo_el).text.strip()
                    else:
                        datos[titulo] = valor
                except:
                    continue

            # 2. Extraer datos de las tablas (Tipo contribuyente, Obligado, Fechas, etc.)
            tablas = self.find_elements(const.TAG_ELEMENT_TABLE, by=By.TAG_NAME)
            for tabla in tablas:
                headers = [th.text.strip() for th in self.find_elements(const.TAG_ELEMENT_TH, by=By.TAG_NAME, parent=tabla)]
                values = [td.text.strip() for td in self.find_elements(const.TAG_ELEMENT_TD, by=By.TAG_NAME, parent=tabla)]
                
                for i in range(len(headers)):
                    if i < len(values):
                        datos[headers[i]] = values[i]

            self.state = const.STATE_SUCCESS
            self._data["ruc_data"] = datos
            return True
        except Exception as e:
            self.error(f"Error extracting RUC data: {str(e)}")
            self.state = const.STATE_ERROR
            return False
    
    def redirect_to_request_ruc(self, url):
        try:
            self.driver.get(url)
            self.wait(const.AWAIT_OPEN)
            return True
        except Exception as e:
            self.error(f"Error redirecting to RUC request page: {str(e)}")
            self.state = const.STATE_ERROR
            return False
        
    def consultar_con_reintento(self, max_intentos=5):
        intentos = 0
        xpath_error = "//span[contains(@class, 'ui-messages-detail') and contains(text(), 'Puntaje bajo')]"
        
        while intentos < max_intentos:
            # Simular un movimiento errático de mouse antes de consultar
            
            self.wait(const.AWAIT_LOCATE_SHORT)
            # 1. Referenciar y hacer clic (Tu código actual)
            if boton := self.wait_for_element_clickable(const.SRI_XPATH_BUTTON_SEARCH):
                self.move(boton)
                self.click(boton)
                print(f"🚀 Intento {intentos + 1}: Clic en Consultar enviado.")

            self.wait(const.AWAIT_SHORT)
            
            # 3. Verificar si apareció el error de puntaje bajo
            mensajes_error = self.find_elements(xpath_error)
            
            if len(mensajes_error) > 0:
                error_texto = mensajes_error[0].text
                self.warn(f"⚠️ Falló: {error_texto}. Reintentando clic...")
                
                # Opcional: Limpiar el mensaje de error anterior para no confundir al bot
                # self._driver.execute_script("document.querySelectorAll('.ui-messages-close').forEach(el => el.click());")
                intentos += 1
                
                 # Pausa táctica antes del siguiente clic
            else:
                # Si NO hay error, verificamos si realmente cargó la info del contribuyente
                if self.wait_for_element(const.SRI_XPATH_MORE_STABLISHMENTS, timeout=const.TIMEOUT_MINIMUM):
                    self.info("✅ Consulta exitosa sin errores.")
                    return True # Éxito total
                
                intentos += 1

        self.info("❌ Se agotaron los intentos. El SRI bloqueó el token permanentemente.")
        return False
    
    def consultar_con_solver(self):
        site_key = self.get_site_key()
        token_valido = self.resolver_capsolver(site_key=site_key)
        
        if token_valido:
            script = f"""
                (function() {{
                    window.token_bypass_sri = '{token_valido}';
                    
                    // 1. Llenar el campo oculto
                    var fields = document.getElementsByName('g-recaptcha-response');
                    for (var i = 0; i < fields.length; i++) {{
                        fields[i].value = window.token_bypass_sri;
                    }}

                    // 2. Parchear con referencia global
                    if (window.grecaptcha && window.grecaptcha.enterprise) {{
                        window.grecaptcha.enterprise.execute = function(siteKey, options) {{
                            console.log('SRI solicitó token para:', options.action);
                            // Retornamos el valor global para evitar el ReferenceError
                            return Promise.resolve(window.token_bypass_sri);
                        }};
                        console.log('✅ Parche aplicado sin errores de referencia.');
                    }}
                }})();
            """
            self.driver.execute_script(script)
            time.sleep(2)
            # 5. Clic final mediante JavaScript
            self.info("🚀 Enviando consulta al SRI...")
            # 3. Hacer clic en el botón Consultar
            boton = self.driver.find_element(By.XPATH, "//button[contains(., 'Consultar')]")
            self.driver.execute_script("arguments[0].click();", boton)

        
            time.sleep(2)
            xpath_error = "//span[contains(@class, 'ui-messages-detail') and contains(text(), 'Puntaje bajo')]"
            # mensajes_error = self._driver.find_elements(By.XPATH, xpath_error)
            mensajes_error = self.find_elements(xpath_error)

            if len(mensajes_error) > 0:
                error_texto = mensajes_error[0].text
                self.info(f"⚠️ Falló: {error_texto}. Reintentando clic...")

            if self.check_if_result_exists():
                return True
            return False
        return False

    def resolve_recaptcha_v3(self, site_key):
        self.info("\n[!] Esperando resolución del captcha...")
        self.info(f"Current url for recaptcha: {self.driver.current_url}")
        response = self._solver.recaptcha(
            sitekey=site_key, 
            url=self.driver.current_url, 
            version='v3', 
            enterprise=1, 
            # action='ruc_consulta',
            action='sri_consulta_publica_ruc',
            # action='ruc_consulta',
            score=0.9,
            # min_score = 0.7,
            # method = 'userrecaptcha'
        )
        
        if token := response.get("code"):
            self.info(f"[+] Captcha resuelto manualmente: {token[:10]}") 
            # self.driver.execute_script(self.get_script_inject_recapctha_token(token=token))
            self.action = const.ACTION_RECAPTCHA, const.STATE_SUCCESS
            return True
                
        return False
    
    def check_if_result_exists(self):
    # Buscamos por el nombre del tag específico
        results = self.find_elements("sri-mostrar-contribuyente", by=By.TAG_NAME)
        return len(results) > 0

    def get_site_key(self):
        try:
            iframe = self.wait_for_element(const.SRI_XPATH_GET_SITE_KEY, by=By.XPATH, timeout=const.TIMEOUT_MINIMUM)
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
        
    def verificar_deteccion(self):
        print("\n--- AUDITORÍA DE INVISIBILIDAD ---")
        self.driver.get("https://bot.sannysoft.com/")
        time.sleep(5) 

        resultados = self.driver.execute_script("""
            return {
                "webdriver": navigator.webdriver,
                "plugins": navigator.plugins.length,
                "languages": navigator.languages
            };
        """)

        print(f"1. Webdriver: {resultados['webdriver']}")
        print(f"2. Plugins: {resultados['plugins']}")
        print(f"3. Idiomas: {resultados['languages']}")

    def resolver_capsolver(self, site_key):
        try:
            ua_real = self.driver.execute_script("return navigator.userAgent")
            # Creamos la tarea para reCAPTCHA v3 Enterprise
            solution = capsolver.solve({
                "type": "ReCaptchaV3EnterpriseTaskProxyLess",
                "websiteURL": self.driver.current_url, # URL exacta del SRI
                "websiteKey": site_key,
                "pageAction": "sri_consulta_publica_ruc", # Cambiar según la acción de la página
                "minScore": 0.9, # El SRI suele ser estricto y pide score alto,
                "userAgent": ua_real
            })
            
            token = solution.get('gRecaptchaResponse')
            print(f"Token obtenido: {token}")
            self.action = const.ACTION_RECAPTCHA, const.STATE_SUCCESS
            return token

        except Exception as e:
            self.state = const.STATE_ERROR
            self.error(f"Error al resolver: {e}")
            return False


    def inyectar_scripts_antideteteccion(self):    
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // 1. Eliminar rastro de WebDriver
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

                // 2. Simular Plugins
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

                // 3. Simular Lenguajes
                Object.defineProperty(navigator, 'languages', { get: () => ['es-EC', 'es', 'en'] });

                // 4. Simular WebGL (Hardware real)
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Open Source Technology Center';
                    if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 550 (SKL GT2)';
                    return getParameter.apply(this, arguments);
                };
            """
        })