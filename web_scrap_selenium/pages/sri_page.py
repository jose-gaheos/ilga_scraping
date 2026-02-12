from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium import webdriver
from config import settings, const, scripts
from recaptcha import solve_recaptcha
from utils.utils import download_image_to_base64, write_like_as_human, escribir_con_error_humano
import time
from selenium.webdriver.common.action_chains import ActionChains
import random
import re

class SRI:
    def __init__(self, url):
        self._driver = webdriver.Chrome(options=settings.get_default_chrome_options())
        self._url = url

        # self.radio_ruc = const.SUPERCIAS_RADIO_RUC
        # self.input_ruc = const.SUPERCIAS_INPUT_RUC
        self.data = {}

    def login(self):
        wait = WebDriverWait(self._driver, 5)
        username = self._driver.find_element(By.ID, const.SRI_ID_INPUT_USERNAME) 
        username.clear()
        username.send_keys("0921839023001")  
        time.sleep(2)
        password = self._driver.find_element(By.ID, const.SRI_ID_INPUT_PASSWORD) 
        password.clear()
        password.send_keys("Armagedon@97")   
        time.sleep(2)
        button_login = self._driver.find_element(By.XPATH, const.SRI_XPATH_BUTTON_LOGIN)
        button_login.click()


    def redirect_to_request_ruc(self, url):
        time.sleep(3)
        self._driver.execute_script(f"window.location.href = '{url}';")


    def start_bot(self):
        # self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #         # Eliminar rastro de WebDriver
        #         try {
        #             Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        #         } catch (e) {}

        #         # Simular Plugins de forma estática (sin romper iframes)
        #         try {
        #             const mockPlugins = [
        #                 { name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
        #                 { name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }
        #             ];
        #             Object.defineProperty(navigator, 'plugins', { get: () => mockPlugins });
        #         } catch (e) {}

        #         # Forzar el idioma
        #         try {
        #             Object.defineProperty(navigator, 'languages', { get: () => ['es-EC', 'es'] });
        #         } catch (e) {}
        #     """
        #     })
        # self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #         # 1. Simular Plugins (Evita el Plugins Length: 0)
        #         # Definimos una estructura que engaña a las pruebas básicas
        #         Object.defineProperty(navigator, 'plugins', {
        #             get: () => {
        #                 var dummy = [1, 2, 3, 4, 5];
        #                 dummy.item = (i) => dummy[i];
        #                 dummy.namedItem = (name) => null;
        #                 return dummy;
        #             }
        #         });

        #         # 2. Corregir Idiomas (De es-419 a es-EC)
        #         Object.defineProperty(navigator, 'languages', {
        #             get: () => ['es-EC', 'es', 'en-US', 'en']
        #         });

        #         # 3. Eliminar rastro de WebDriver (Ya lo tienes, pero por seguridad)
        #         Object.defineProperty(navigator, 'webdriver', {
        #             get: () => undefined
        #         });
        #     """
        #     })

        # 1. Visita la página de prueba
        # self._driver.get("https://bot.sannysoft.com/")

        
        
        self.inyectar_scripts_antideteteccion()
        # self.verificar_deteccion()
        # self.verificar_deteccion()

       
        # Justo después de crear el driver
        
        self._driver.get(self._url)

        # self._driver.execute_script(f"""
        #     // Guardamos la función original para no romper el sitio
        #     var originalExecute = grecaptcha.enterprise.execute;

        #     // Sobrescribimos con nuestra función de rastreo
        #     grecaptcha.enterprise.execute = function(siteKey, options) {{
        #         console.log("¡reCAPTCHA detectado!");
        #         console.log("Site Key:", siteKey);
        #         console.log("Action:", options.action); // Aquí obtienes el nombre de la acción
                
        #         // Llamamos a la función original para que el formulario siga funcionando
        #         return originalExecute.apply(this, arguments);
        #     }};
        # """)

    def inyectar_scripts_antideteteccion(self):
        # Usamos comillas simples para el JS y evitamos comentarios con '#' (JS usa //)
        # self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        #     "source": """
        #         Object.defineProperty(navigator, 'webdriver', {
        #             get: () => undefined
        #         })
        #     """
        # })        
        script_inyectado = """
            window.addEventListener('DOMContentLoaded', (event) => {
                if (window.grecaptcha && window.grecaptcha.enterprise) {
                    const originalExecute = grecaptcha.enterprise.execute;
                    grecaptcha.enterprise.execute = function(siteKey, options) {
                        window.lastRecaptchaAction = options.action; // Guardamos en window para leerlo luego
                        console.log("Action capturada:", options.action);
                        return originalExecute.apply(this, arguments);
                    };
                }
            });
        """
        
        self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
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

                // --- 5. Interceptar reCAPTCHA Enterprise ---
                window.grecaptcha_data = { action: null, siteKey: null }; // Contenedor para los datos

                // Usamos un Proxy o un Setter para detectar cuándo se define grecaptcha en la página
                let enterpriseProxy = undefined;
                Object.defineProperty(window, 'grecaptcha', {
                    configurable: true,
                    enumerable: true,
                    get: () => enterpriseProxy,
                    set: (val) => {
                        enterpriseProxy = val;
                        // Si el objeto enterprise existe, interceptamos su método execute
                        if (enterpriseProxy && enterpriseProxy.enterprise) {
                            const originalExecute = enterpriseProxy.enterprise.execute;
                            enterpriseProxy.enterprise.execute = function(siteKey, options) {
                                window.grecaptcha_data.siteKey = siteKey;
                                window.grecaptcha_data.action = options.action;
                                console.log("CAPTURED ACTION:", options.action);
                                return originalExecute.apply(this, arguments);
                            };
                        }
                    }
                });
            """
        })

        

    def verificar_deteccion(self):
        print("\n--- AUDITORÍA DE INVISIBILIDAD ---")
        self._driver.get("https://bot.sannysoft.com/")
        time.sleep(5) 

        resultados = self._driver.execute_script("""
            return {
                "webdriver": navigator.webdriver,
                "plugins": navigator.plugins.length,
                "languages": navigator.languages
            };
        """)

        

        print(f"1. Webdriver: {resultados['webdriver']}")
        print(f"2. Plugins: {resultados['plugins']}")
        print(f"3. Idiomas: {resultados['languages']}")

    def enter_ruc_or_ci(self, identification):
        

        wait = WebDriverWait(self._driver, 10)
        try:
            # 1. Ingresar el RUC
            input_ruc = wait.until(EC.presence_of_element_located((By.ID, const.SRI_ID_INPUT_SEARCH)))
            input_ruc.clear() # Limpieza preventiva
            input_ruc.send_keys(identification)

            # boton_consultar = wait.until(EC.element_to_be_clickable((By.XPATH, const.SRI_XPATH_BUTTON_SEARCH)))
            # boton_consultar.click()
            # 2. Ejecutar la lógica de reintentos
            # IMPORTANTE: Guardamos el resultado (True/False) del reintento
            # fue_exitoso = self.consultar_con_reintento(max_intentos=10)
            fue_exitoso = self.consultar_con_twocaptch()
            # fue_exitoso = self.check_if_result_exists()
            return fue_exitoso # Le dice a run_test si puede seguir o no

        except Exception as e:
            print(f"❌ Error crítico al ingresar identificación: {e}")
            return False
    
    def consultar_con_twocaptch(self):
        site_key = self.get_site_key()
        token_valido = self.resolve_captcha_v3(site_key=site_key, page_url=self._url)
        if token_valido:
            script = f"""
                (function() {{
                    window.tokenUsado = false;
                    const tokenValido = '{token_valido}'; // Usamos el nombre consistente
                    window.token_bypass_sri = tokenValido;
                    
                    console.log('Iniciando bypass de reCAPTCHA...');

                    // 1. Llenar campos ocultos (algunas versiones de PrimeNG los usan)
                    const selectors = ['[name="g-recaptcha-response"]', '#g-recaptcha-response-enterprise', '[name="g-recaptcha-response-enterprise"]'];
                    selectors.forEach(selector => {{
                        document.querySelectorAll(selector).forEach(el => {{
                            el.value = tokenValido;
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        }});
                    }});

                    // 2. Parchear el objeto grecaptcha
                    if (window.grecaptcha && window.grecaptcha.enterprise) {{
                        const originalExecute = window.grecaptcha.enterprise.execute;

                        window.grecaptcha.enterprise.execute = function(siteKey, options) {{
                            console.log('Interceptada ejecución para acción:', options.action);
                            
                            if (!window.tokenUsado) {{
                                window.tokenUsado = true;
                                console.log('✅ Entregando token de 2Captcha para action:', options.action);
                                return Promise.resolve(tokenValido);
                            }} else {{
                                console.log('⚠️ Token ya usado, permitiendo ejecución original para evitar DUPE');
                                return originalExecute.apply(this, [siteKey, options]);
                            }}
                        }};
                        console.log('✅ Interceptor de reCAPTCHA Enterprise activo.');
                    }} else {{
                        console.error('❌ No se encontró grecaptcha.enterprise en la página.');
                    }}
                    
                    console.log('🚀 Configuración completada.');
                }})();
            """
            self._driver.execute_script(script)
            time.sleep(3)
            # 5. Clic final mediante JavaScript
            print("🚀 Enviando consulta al SRI...")
            # 3. Hacer clic en el botón Consultar
            boton = self._driver.find_element(By.XPATH, "//button[contains(., 'Consultar')]")
            self._driver.execute_script("arguments[0].click();", boton)


            time.sleep(2)
            xpath_error = "//span[contains(@class, 'ui-messages-detail') and contains(text(), 'Puntaje bajo')]"
            mensajes_error = self._driver.find_elements(By.XPATH, xpath_error)
            
            if len(mensajes_error) > 0:
                error_texto = mensajes_error[0].text
                print(f"⚠️ Falló: {error_texto}. Reintentando clic...")

            if self.check_if_result_exists():
                return True
            return False
        return False

    def consultar_con_reintento(self, max_intentos=3):
        intentos = 0
        xpath_error = "//span[contains(@class, 'ui-messages-detail') and contains(text(), 'Puntaje bajo')]"
        
        while intentos < max_intentos:
            # Simular un movimiento errático de mouse antes de consultar
            script_movimiento = """
                var event = new MouseEvent('mousemove', {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': 100,
                    'clientY': 100
                });
                document.dispatchEvent(event);
            """
            self._driver.execute_script(script_movimiento)
            time.sleep(3)
            # 1. Referenciar y hacer clic (Tu código actual)
            boton = self._driver.find_element(By.XPATH, "//button[contains(., 'Consultar')]")
            self._driver.execute_script("arguments[0].click();", boton)
            print(f"🚀 Intento {intentos + 1}: Clic en Consultar enviado.")
            
            # 2. Esperar a que el servidor responda (ajusta el tiempo si el SRI está lento)
            time.sleep(2.5)
            
            # 3. Verificar si apareció el error de puntaje bajo
            mensajes_error = self._driver.find_elements(By.XPATH, xpath_error)
            
            if len(mensajes_error) > 0:
                error_texto = mensajes_error[0].text
                print(f"⚠️ Falló: {error_texto}. Reintentando clic...")
                
                # Opcional: Limpiar el mensaje de error anterior para no confundir al bot
                self._driver.execute_script("document.querySelectorAll('.ui-messages-close').forEach(el => el.click());")
                intentos += 1
                time.sleep(3)
                 # Pausa táctica antes del siguiente clic
            else:
                # Si NO hay error, verificamos si realmente cargó la info del contribuyente
                if self.check_if_result_exists():
                    return True # Éxito total
                
                intentos += 1

        print("❌ Se agotaron los intentos. El SRI bloqueó el token permanentemente.")
        return False

    def check_if_result_exists(self):
    # Buscamos por el nombre del tag específico
        results = self._driver.find_elements(By.TAG_NAME, "sri-mostrar-contribuyente")
        return len(results) > 0

    def check_captcha_error(self, driver):
        try:
            # Espera corta para ver si aparece el mensaje de error
            wait = WebDriverWait(driver, 5)
            mensaje_error = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'ui-messages-detail')]")
            ))
            
            texto_error = mensaje_error.text
            if "Puntaje bajo" in texto_error:
                print(f"⚠️ Error de validación detectado: {texto_error}")
                return True
                
        except TimeoutException:
            # Si no aparece el mensaje, asumimos que la consulta fue exitosa
            return False
        return False

    def show_establishments(self):
        wait = WebDriverWait(self._driver, 5)
        
        try:
            self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            xpath_boton = "//button[.//span[contains(., 'Mostrar establecimientos')]]"
            boton = wait.until(EC.presence_of_element_located((By.XPATH, xpath_boton)))
            boton.click()

            print("✅ Establecimientos desplegados correctamente.")
            
        except TimeoutException:
            self._driver.save_screenshot("debug_sri_fallo.png")
            print("❌ Error: El botón no apareció a tiempo. Captura guardada en debug_sri_fallo.png")
            raise
    
    def print_screen(self):
        self._driver.execute_script('window.print();')

        print("PDF guardado automáticamente en la carpeta configurada.")

    def get_site_key(self):
        try:
            wait_iframe = WebDriverWait(self._driver, 10)
            # 1. Localizar el iframe de Google reCAPTCHA
            iframe = wait_iframe.until(EC.presence_of_element_located((By.XPATH, const.SRI_XPATH_GET_SITE_KEY)))
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
        
    def resolve_captcha_v3(self, site_key, page_url):
        print("\n[!] Esperando resolución del captcha...")
        token = solve_recaptcha.solve_recaptcha_v3(site_key=site_key, page_url=page_url)
        print(f"Token recaptcha {token[:30]}")
            
        return token
    
