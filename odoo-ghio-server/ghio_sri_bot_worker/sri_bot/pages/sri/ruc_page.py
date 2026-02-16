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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from ...core.capsolver import CapSolverService

import random

from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

capsolver.api_key = os.getenv('API_KEY_CAPSOLVER')
api_key_capsolver = os.getenv('API_KEY_CAPSOLVER')

class RucPage(BasePage):
    def __init__(self, manager, data, extra_ci=None, solver=None):
        super().__init__(manager)
        self._extra_ci = extra_ci
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self._data = data
        self._capsolver = CapSolverService(api_key_capsolver)
 

    def run(self):

        if not self.open(const.CONSULTA_RUC_SRI_URL):
            self.action = const.ACTION_HOME, const.STATE_FAILED
            return False

        # EL TRUCO: El script se detiene aquí
        # print("Navegador listo. Entra a http://localhost:7900 y loguéate.")
        # input(">>> Presiona ENTER cuando hayas terminado el login para continuar...")
        # self.inyectar_scripts_antideteteccion()

        if not self.ensure_action(const.ACTION_HOME, const.STATE_INITIAL):
            print("Action or state not valid for SearchPage Juditial Function")
            return False

        self.action = const.ACTION_HOME, const.STATE_PENDING
       
        selector_ruc = '[aria-label="Seleccionar búsqueda por RUC"]'

        
        if ruc_button := self.wait_for_element_clickable(selector_ruc, by=By.CSS_SELECTOR):
            self.move(ruc_button)
            # self.random_move(ruc_button)
            self.click(ruc_button)
            self.wait(const.AWAIT_SHORT)
        

        if input_ruc := self.wait_for_element(const.SRI_ID_INPUT_SEARCH, by=By.ID):
            # self.move(input_ruc)
            self.wait(const.AWAIT_MEDIUM)
            self.random_move(input_ruc)
            self.click(input_ruc)
            if self._extra_ci:
                self.send_keys(input_ruc, self._extra_ci)
                #escribir_con_error_humano(elemento= input_ruc, texto = self._extra_ci, error_delete=-1)
            else:
                self.info(f"No extra CI provided for RUC search: {self._extra_ci}")
                self.state = const.STATE_INVALID
                return False
        else:
            self.error('RUC input field not found')
            self.state = const.STATE_INVALID
            return False
        

        if not self.consultar_con_reintento(max_intentos=5):
                self.info("RUC data retrieved error after retries")
                self.state = const.STATE_ERROR
                return False
        
        if self.extraer_datos_sri() and self.ensure_action(const.ACTION_HOME, const.STATE_SUCCESS):
            self.info("RUC data extraction completed successfully")
            return True

        # self.info("RUC data retrieved successfully")
        
        
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
                    
                    # Limpieza para el caso del Representante Legal que tiene sub-campos
                    if "Nombre/Razón Social" in titulo:
                        # Caso específico para la estructura anidada del representante
                        datos["Representante_Nombre"] = self.find_element(const.SRI_XPATH_LEGAL_NAME, parent=titulo_el).text.strip()
                    elif "Identificación" in titulo:
                        datos["Representante_ID"] = self.find_element("./following-sibling::div[1]", parent=titulo_el).text.strip()
                    else:
                        try:
                            if valor := titulo_el.find_element(const.SRI_XPATH_DIV_VALUE, by=By.XPATH).text.strip():
                                datos[titulo] = valor
                            # Si lo encuentra, haces algo con él aquí
                        except NoSuchElementException:
                            # Si no lo encuentra, ignora el error y continúa
                            pass
                       
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
        

    def random_move(self, target_element=None):
        action = ActionChains(self.driver)
        # Mover a un punto aleatorio cerca del botón antes de clickear
        action.move_by_offset(random.randint(10, 100), random.randint(10, 100))
        action.pause(random.uniform(0.5, 1.5))
        action.click(target_element).perform()

    def check_bot_status(self):
        # 1. SNEAKY: Prueba de detección de Selenium/WebDriver
        print("Verificando en SNEAKY...")
        self.driver.get("https://pixelscan.net/")
        time.sleep(5) # Espera a que termine el análisis
        
        # 2. BROWSERLEAKS: Prueba de huella digital (IP, WebGL, RTC)
        print("Verificando en BrowserLeaks...")
        self.driver.execute_script("window.open('https://browserleaks.com/ip', '_blank');")
        time.sleep(3)

        # 3. ANTICAPTCHA / CAPSOLVER CHECK: Ver si la extensión está inyectando código
        print("Verificando CapSolver Score...")
        self.driver.execute_script("window.open('https://antcpt.com/score_detector/', '_blank');")
        
        print("Revisa las pestañas abiertas para ver tu calificación.")

    def verificar_deteccion(self):
        print("\n--- AUDITORÍA DE INVISIBILIDAD ---")
        self.driver.execute_script("window.open('https://bot.sannysoft.com/', '_blank');")
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
           
        
    def consultar_con_reintento(self, max_intentos=5):
        intentos = 0
        xpath_error = "//span[contains(@class, 'ui-messages-detail') and contains(text(), 'Puntaje bajo')]"
        
        while intentos < max_intentos:
            element = self.driver.find_element(By.XPATH, "//button[contains(@class, 'ui-button')]//span[text()='Consultar']")

            # Mover el mouse al botón para que el script de Akamai registre actividad real
            ActionChains(self.driver).move_to_element(element).pause(0.5).perform()
            self.driver.execute_script("arguments[0].click();", element)
            self.info(f"🚀 Intento {intentos + 1}: Clic en Consultar enviado.")

            self.wait(const.AWAIT_SHORT)
            
            #Verificar si apareció el error de puntaje bajo
            mensajes_error = self.find_elements(xpath_error)
            
            if len(mensajes_error) > 0:
                error_texto = mensajes_error[0].text
                self.warn(f"⚠️ Falló: {error_texto}. Reintentando clic...")
                
                intentos += 1
            else:
                # Si NO hay error, verificamos si realmente cargó la info del contribuyente
                if self.wait_for_element(const.SRI_XPATH_MORE_STABLISHMENTS, timeout=const.TIMEOUT_MINIMUM):
                    self.info("✅ Consulta exitosa sin errores.")
                    self.action = const.ACTION_HOME, const.STATE_SUCCESS
                    return True # Éxito total
                
                self.wait(const.AWAIT_SHORT)
                intentos += 1

        self.info("❌ Se agotaron los intentos. El SRI bloqueó el token permanentemente.")
        return False

    def resolve_recaptcha_v3(self, site_key):
        self.driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(0.5)
        self.driver.execute_script("window.scrollTo(0, 0);")
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
            return token or None
                
        return False
    
    def check_if_result_exists(self):
    # Buscamos por el nombre del tag específico
        results = self.find_elements("sri-mostrar-contribuyente", by=By.TAG_NAME)
        if len(results) > 0:
            self.info("Se encontraron resultados....")
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


    def resolver_capsolver(self, site_key, ruc):
        try:
            # 1. Crear la tarea y obtener token
            task_id = self._capsolver.create_task(
                website_url="https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc",
                website_key=site_key,
                task_type="ReCaptchaV3EnterpriseTaskProxyLess",
                # page_action=""
                page_action="sri_consulta_publica_ruc"
            )
            token_valido = self._capsolver.get_task_result(task_id)
            self.info(f"El token obtenido es: {token_valido[:30]}...")

            # 2. Script mejorado con Reintentos y Visibilidad Forzada
            # Combinamos debug y final en uno solo para evitar múltiples ejecuciones de red
            script_final = f"""
            (function() {{
                const token = '{token_valido}';
                console.log('--- Iniciando inyección de CapSolver ---');

                function inyectar() {{
                    // 1. Llenar inputs ocultos (g-recaptcha-response)
                    const targets = document.querySelectorAll('textarea[name="g-recaptcha-response"], input[name="g-recaptcha-response"]');
                    targets.forEach(el => {{
                        el.value = token;
                        console.log('Token insertado en input:', el.id || 'sin id');
                    }});

                    // 2. Interceptar ReCaptcha Enterprise
                    if (window.grecaptcha && window.grecaptcha.enterprise) {{
                        window.grecaptcha.enterprise.execute = function(s, o) {{
                            console.log('✅ Interceptado execute para acción:', o.action);
                            return Promise.resolve(token);
                        }};
                        return true;
                    }}
                    return false;
                }}

                // Intentar inyectar de inmediato y repetir si no se encuentra el objeto
                if (!inyectar()) {{
                    console.log('⚠️ grecaptcha no listo, programando reintentos...');
                    let intentos = 0;
                    const i = setInterval(() => {{
                        intentos++;
                        if (inyectar() || intentos > 20) {{
                            clearInterval(i);
                            console.log('Inyección finalizada tras ' + intentos + ' intentos');
                        }}
                    }}, 500);
                }} else {{
                    console.log('🚀 Inyección exitosa al primer intento');
                }}
            }})();
            """
            
            #self.driver.execute_script(script_final)

            # self.consultar_directo_sri(ruc=ruc, token_capsolver=token_valido)
            
            # 3. Pequeña espera para que el JS se asiente
            import time
            time.sleep(1) 
            
            return True

        except Exception as e:
            self.error(f"Error al resolver: {e}")
            return False
    # def resolver_capsolver(self, site_key):
    #     try:
           

    #         task_id = self._capsolver.create_task(
    #             website_url="https://srienlinea.sri.gob.ec",
    #             website_key=site_key,
    #             task_type="ReCaptchaV3EnterpriseTaskProxyLess",
    #             page_action="sri_consulta_publica_ruc"
    #         )

    #         token_valido = self._capsolver.get_task_result(task_id)

    #         self.info(f"El token obtenido es: {token_valido[:30]}" )

    #         script_debug = f"""
    #             if (window.grecaptcha && window.grecaptcha.enterprise) {{
    #                 window.grecaptcha.enterprise.execute = function(siteKey, options) {{
    #                     return Promise.resolve('{token_valido}');
    #                 }};
    #                 return "SUCCESS: Interceptado";
    #             }} else {{
    #                 return "ERROR: grecaptcha.enterprise no encontrado";
    #             }}
    #         """
    #         resultado = self.driver.execute_script(script_debug)
    #         print(f"Resultado de la inyección: {resultado}")

    #         script_final = f"""
    #             (function() {{
    #                 const token = '{token_valido}';
                    
    #                 // Llenar todos los campos g-recaptcha-response que existan
    #                 document.getElementsByName('g-recaptcha-response').forEach(el => {{
    #                     el.value = token;
    #                 }});

    #                 // Sobrescribir la ejecución de Enterprise para que devuelva nuestro token de CapSolver
    #                 if (window.grecaptcha && window.grecaptcha.enterprise) {{
    #                     window.grecaptcha.enterprise.execute = function(siteKey, options) {{
    #                         console.log('Interceptando petición para:', options.action);
    #                         return Promise.resolve(token);
    #                     }};
    #                 }}
    #             }})();
    #             """
    #         self.driver.execute_script(script_final)
    #         return True
    #         # ua_real = self.driver.execute_script("return navigator.userAgent")

    #         # # proxy_address = f"{os.getenv('PROXY_HOST')}:{os.getenv('PROXY_PORT')}" 
    #         # # print("Using proxy address:", proxy_address)
    #         # # Creamos la tarea para reCAPTCHA v3 Enterprise
    #         # solution = capsolver.solve({
    #         #     "type": "ReCaptchaV3EnterpriseTaskProxyLess",
    #         #     "websiteURL": self.driver.current_url, # URL exacta del SRI
    #         #     "websiteKey": site_key,
    #         #     "pageAction": "sri_consulta_publica_ruc", # Cambiar según la acción de la página
    #         #     "minScore": 0.9, # El SRI suele ser estricto y pide score alto,
    #         #     # "proxy": proxy_address  # Sincronización de IP
    #         # })
            
    #         # token = solution.get('gRecaptchaResponse')
    #         # print(f"Token obtenido: {token[:10]}")
    #         # self.action = const.ACTION_RECAPTCHA, const.STATE_SUCCESS
    #         # return token

    #     except Exception as e:
    #         self.state = const.STATE_ERROR
    #         self.error(f"Error al resolver: {e}")
    #         return False


    def inyectar_scripts_antideteteccion(self):    
        self.info("Se inyectaron scripts de antidetección...")
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