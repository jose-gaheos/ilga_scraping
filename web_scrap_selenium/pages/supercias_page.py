from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from selenium import webdriver
from config import settings, const
from recaptcha import solve_recaptcha
from utils.utils import download_image_to_base64
import time
class Supercias:
    def __init__(self, url):
        self._driver = webdriver.Chrome(options=settings.get_default_chrome_options())
        self._url = url

        self.radio_ruc = const.SUPERCIAS_RADIO_RUC
        self.input_ruc = const.SUPERCIAS_INPUT_RUC
        self.data = {}

    def start_bot(self):
        self._driver.get(self._url)

    def enter_ruc_or_ci(self, identification):
        wait = WebDriverWait(self._driver, 10)

        radio = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.radio_ruc)))
        radio.click()
        time.sleep(0.5)

        wait.until(EC.element_to_be_clickable((By.ID, self.input_ruc))).send_keys(identification)

        time.sleep(0.5)
        wait.until(EC.presence_of_element_located((By.XPATH, const.SUPERCIAS_FIRST_RESULT_RUC))).click()

    
    def select_first_result(self):
        wait = WebDriverWait(self._driver, 10)

    def get_image_captcha_base64_to_login(self, query_selector):
        wait = WebDriverWait(self._driver, 5)
        image_captcha = wait.until(EC.presence_of_element_located((By.ID, query_selector)))
        url_image = image_captcha.get_attribute("src")
        print("image: ", url_image)

        image_base64 = download_image_to_base64(url_image=url_image)

        return image_base64


    def resolve_captcha(self, image_base64):
        code_captcha = solve_recaptcha.solve_image_captcha(image_base64=image_base64)
        print('Response: ', code_captcha)
        return code_captcha

        

    def login(self, code):
        wait = WebDriverWait(self._driver, 5)
        input_captcha = wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_INPUT_CAPTCHA_LOGIN)))
        if not input_captcha:
            print('No se econtro aun el input del captcha')
            return
        input_captcha.clear()
        input_captcha.send_keys(code)

        button_search = self._driver.find_element(By.ID, const.SUPERCIAS_BUTTON_SEARCH_LOGIN)
        button_search.click()


    def exist_menu_main_page(self):
        wait = WebDriverWait(self._driver, 5)

        menu = wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_MAIN_MENU)))
        return True if menu else None
    
    def get_general_information(self):
        wait = WebDriverWait(self._driver, 10)

        accordion_gen_information = wait.until(EC.presence_of_element_located((By.XPATH, const.SUPERCIAS_ACCORDION_GENERAL_INFORMATION)))

        divs_internos = accordion_gen_information.find_elements(By.XPATH, "./div")

        general_information = {}
        clave_anterior = ""
        for div in divs_internos:
            clase = div.get_attribute('class')
            
            if "ui-accordion-header" in clase:
                header = div.find_element(By.CSS_SELECTOR, "div span")
                header_text = header.get_attribute("textContent").strip()
            
                # Si el texto sigue vacío, intentamos capturar todo el texto del div padre
                if not header_text:
                    header_text = div.text.strip()
                general_information[header_text] = {}
                clave_anterior = header_text

            if "ui-accordion-content" in clase:
                rows = div.find_elements(By.XPATH, "./table/tbody/tr")
                datos_seccion = {}
                for item_row in rows:
                    etiquetas = item_row.find_elements(By.CLASS_NAME, "columna1")

                    for celda_clave in etiquetas:
                        try:

                            clave = celda_clave.get_attribute("innerText").strip()

                            if clave:
                                # Localizar la celda de valor (columna2) que está justo al lado
                                # Se usa el XPath "following-sibling" para ser obtener el hermano de columna1
                                celda_valor = celda_clave.find_element(By.XPATH, "./following-sibling::td")
                                
                                valor = celda_valor.find_element(By.CSS_SELECTOR, "input, textarea").get_attribute("value")

                                datos_seccion[clave] = valor.replace('\xa0', ' ').strip()
                                
                        except Exception as e:
                            # Si una celda está vacía o no tiene input, pasamos a la siguiente
                            continue

                general_information[clave_anterior] = datos_seccion

        self.data[const.SUPERCIAS_KEY_GENERAL_INFORMATION] = general_information

    def verify_exists_captcha(self):
        if self.exist_dialog_captcha():
                print("Captcha detectado, resolviendo...")
                self.resolve_dialog_captcha()

    def get_annual_information(self):
        wait = WebDriverWait(self._driver, 10)

        self.verify_exists_captcha()

        if self.exist_menu_main_page():
            wait.until(EC.element_to_be_clickable((By.ID, const.SUPERCIAS_ITEM_ANNUAL_INFORMATION))).click()

            self.verify_exists_captcha()
            try:
                # Esperamos hasta que cualquiera de los dos esté presente
                wait.until(lambda d: d.find_elements(By.ID, const.SUPERCIAS_CONTAINER_TABLE_ANNUAL_INFORMATION) or 
                                    d.find_elements(By.CSS_SELECTOR, const.SUPERCIAS_DIALOG_CAPTCHA))
            except TimeoutException:
                print("Ni la tabla ni el captcha aparecieron a tiempo")
            
            self.verify_exists_captcha()

            wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_CONTAINER_TABLE_ANNUAL_INFORMATION)))

            input_document = wait.until(EC.element_to_be_clickable((By.XPATH, const.SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT)))
            input_document.send_keys("INTEGRAL")

            time.sleep(3)

            rows_estado_resultado_integral = self._driver.find_elements(By.XPATH, const.SUPERCIAS_ROWS_ANNUAL_INFORMATION)

            headers_table = self._driver.find_elements(By.XPATH, const.SUPERCIAS_XPATH_HEADER_TITLE_ANNUAL_INFORMATION)

            headers = [item_header.text.strip().lower() for item_header in headers_table]

            print(headers)

            lista_estado_resultado, list_er_integral_pdf = self.get_annual_information_pdf(
                rows=rows_estado_resultado_integral,
                headers=headers
            )

            self.execute_download_pdf(elements=list_er_integral_pdf[:3])

            time.sleep(1)
            input_document = wait.until(EC.element_to_be_clickable((By.XPATH, const.SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT)))
            input_document.clear()
            input_document.send_keys("BALANCE")

            time.sleep(3)

            rows_balances = self._driver.find_elements(By.XPATH, const.SUPERCIAS_ROWS_ANNUAL_INFORMATION)
            lista_balances, list_balance_pdf = self.get_annual_information_pdf(
                rows=rows_balances,
                headers=headers
            )

            self.execute_download_pdf(elements=list_balance_pdf[:3])
            
            
            
    

    def get_annual_information_pdf(self, rows, headers ):
        lista_informacion = []
        elements_to_download_pdf = []

        for row in rows:
                # 3. Extraer todas las celdas (td) de la fila actual
                cols = row.find_elements(By.TAG_NAME, const.TAG_ELEMENT_TD)

                nombre_archivo = f"{cols[0].text.strip()} {cols[2].text.strip()}"

                # Verificamos que no sea una fila vacía o de "No hay datos"
                if len(cols) > 1:
                    try:
                        link_pdf = cols[-1].find_element(By.TAG_NAME, const.TAG_ELEMENT_A)
                        id_pdf = link_pdf.get_attribute("id")
                        elements_to_download_pdf.append({
                            'name': nombre_archivo,
                            'id_pdf': id_pdf
                        })
                    except:
                        print("Error get id_pdf: ")
                        pass
                        # elements_to_download_pdf.append(None)
                    
                    datos_fila = {headers[i]: cols[i].text.strip() for i in range(len(headers))}
                    print('datos_fila: ', datos_fila)
                    lista_informacion.append(datos_fila)
                    print(f"Procesado: {datos_fila['nombre documento']} - {datos_fila['año']}")

        return lista_informacion, elements_to_download_pdf



    
    def get_shareholder_data(self):
        wait = WebDriverWait(self._driver, 10)

        self.verify_exists_captcha()

        if self.exist_menu_main_page():
            item_accionistas = wait.until(EC.element_to_be_clickable((By.ID, const.SUPERCIAS_ITEM_ACCIONISTAS)))
            item_accionistas.click()

            self.verify_exists_captcha()
            try:
            # Esperamos hasta que cualquiera de los dos esté presente
                wait.until(lambda d: d.find_elements(By.ID, const.SUPERCIAS_TABLE_BODY_ACCIONISTAS) or 
                                    d.find_elements(By.CSS_SELECTOR, const.SUPERCIAS_DIALOG_CAPTCHA))
            except TimeoutException:
                print("Ni la tabla ni el captcha aparecieron a tiempo.")
                return
            
            self.verify_exists_captcha()
                # Tras resolver el captcha, la tabla puede tardar un poco más en cargar
            wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_TABLE_BODY_ACCIONISTAS)))

            rows = self._driver.find_elements(By.XPATH, f"{const.SUPERCIAS_ROWS_ACCIONISTAS}/tr")

            lista_accionistas = []

            for row in rows:
                # 3. Extraer todas las celdas (td) de la fila actual
                cols = row.find_elements(By.TAG_NAME, "td")
            
                # Verificamos que no sea una fila vacía o de "No hay datos"
                if len(cols) > 1:
                    datos_fila = {
                        "no": cols[0].text.strip(),
                        "identificacion": cols[1].text.strip(),
                        "nombre": cols[2].text.strip(),
                        "nacionalidad": cols[3].text.strip(),
                        "tipo_inversion": cols[4].text.strip(),
                        "capital": cols[5].text.strip(),
                        "restriccion": cols[6].text.strip()
                    }
                    lista_accionistas.append(datos_fila)
                    # print(f"Procesado: {datos_fila['nombre']}")
            self.data[const.SUPERCIAS_KEY_SHAREHOLDERS] = lista_accionistas


    def get_current_administrators_data(self):
        wait = WebDriverWait(self._driver, 10)

        self.verify_exists_captcha()

        if self.exist_menu_main_page():
            item_accionistas = wait.until(EC.element_to_be_clickable((By.ID, const.SUPERCIAS_ITEM_CURRENT_ADMINISTRATORS)))
            item_accionistas.click()

            self.verify_exists_captcha()

            try:
            # Esperamos hasta que cualquiera de los dos esté presente
                wait.until(lambda d: d.find_elements(By.ID, const.SUPERCIAS_TABLE_BODY_CURRENT_ADMINISTRATORS) or 
                                    d.find_elements(By.CSS_SELECTOR, const.SUPERCIAS_DIALOG_CAPTCHA))
            except TimeoutException:
                print("Ni la tabla ni el captcha aparecieron a tiempo.")
                return
            
            self.verify_exists_captcha()
            # Tras resolver el captcha, la tabla puede tardar un poco más en cargar
            wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_TABLE_BODY_CURRENT_ADMINISTRATORS)))

            rows = self._driver.find_elements(By.XPATH, const.SUPERCIAS_ROWS_CURRENT_ADMINISTRATORS)

            headers_table = self._driver.find_elements(By.XPATH, const.SUPERCIAS_HEADER_CURRENT_ADMINISTRATORS)

            headers = []

            for item_header in headers_table:
                header_text = item_header.text.strip().lower()
                headers.append(header_text)
            print(headers)
            
            lista_administradores = []

            elements_to_download_pdf = []

            for row in rows:
                # 3. Extraer todas las celdas (td) de la fila actual
                cols = row.find_elements(By.TAG_NAME, const.TAG_ELEMENT_TD)
            
                # Verificamos que no sea una fila vacía o de "No hay datos"
                if len(cols) > 1:
                    #Pos 1 es el nombre
                    nombre_admin = f"{cols[3].text.strip()} {cols[1].text.strip()}"

                    try:
                        link_pdf = cols[-1].find_element(By.TAG_NAME, const.TAG_ELEMENT_A)
                        id_pdf = link_pdf.get_attribute("id")
                        elements_to_download_pdf.append({
                            'name': nombre_admin,
                            'id_pdf': id_pdf
                        })
                    except:
                        print("Error get id_pdf: ")
                        pass
                        # elements_to_download_pdf.append(None)
                    
                    datos_fila = {headers[i]: cols[i].text.strip() for i in range(len(headers))}

                    lista_administradores.append(datos_fila)
                    print(f"Procesado: {datos_fila['nombre']}")

            self.execute_download_pdf(elements=elements_to_download_pdf)

            self.data[const.SUPERCIAS_KEY_CURRENT_ADMINISTRATORS] = lista_administradores


    def execute_download_pdf(self, elements):

        for item in elements:
                name = str(item.get('name')).replace(" ", "_").upper()
                id_pdf = item.get('id_pdf')
                if id_pdf:
                    try:
                        print(f"Iniciando descarga...")
                        
                        # Buscamos el elemento de nuevo por ID (más seguro)
                        btn = self._driver.find_element(By.ID, id_pdf)

                        # self._driver.execute_script("arguments[0].setAttribute('target', '_blank');", btn)
                        self._driver.execute_script("arguments[0].scrollIntoView();", btn)
                        btn.click()

                        if self.exist_dialog_captcha():
                            print("Captcha detectado, resolviendo...")
                            self.resolve_dialog_captcha()

                        # --- NUEVA LÓGICA PARA EXTRAER Y DESCARGAR EL PDF ---
                        try:
                            # 3. Esperar a que el visor (object) aparezca en el DOM
                            # El selector apunta al object dentro del panel que mencionaste
                            print("Esperando a que el visor PDF cargue el archivo...")
                            pdf_object = WebDriverWait(self._driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, const.SUPERCIAS_PANEL_PDF_OBJECT))
                            )

                            # 4. Extraer la URL del atributo 'data'
                            pdf_url_relativa = pdf_object.get_attribute("data")
                            
                            if pdf_url_relativa:
                                dominio = const.SUPERCIAS_URL_DOMAIN
                                # Verificamos si la URL ya es completa o si es relativa
                                if pdf_url_relativa.startswith("http"):
                                    url_completa = pdf_url_relativa
                                else:
                                    # Solo concatenamos si no tiene el dominio
                                    url_completa = dominio + pdf_url_relativa
                                
                                print(f"URL corregida: {url_completa}")

                                if self.exist_dialog_captcha():
                                    print("Captcha detectado, resolviendo...")
                                    self.resolve_dialog_captcha()

                                self.check_modal_firma_electronica()

                                file_name = f"{name}.pdf"
                                # 4. DESCARGA SILENCIOSA mediante JavaScript
                                # Esto evita que el navegador cambie de página o se ponga en "data:,"
                                print("Iniciando descarga silenciosa...")
                                self._driver.execute_script(f"""
                                    var link = document.createElement('a');
                                    link.href = '{url_completa}';
                                    link.download = '{file_name}';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                """)

                                # 5. CERRAR EL MODAL (Paso vital para que no estorbe al siguiente clic)
                                # Usamos JS para cerrar el modal de PrimeFaces sin buscar el botón X
                                cerrar_modal = WebDriverWait(self._driver, 5).until(EC.element_to_be_clickable((By.XPATH, const.SUPERCIAS_PDF_BUTTON_CLOSE)))
                                cerrar_modal.click()
                                # Esperar a que el bloqueo gris desaparezca
                                WebDriverWait(self._driver, 5).until(
                                    EC.invisibility_of_element_located((By.CLASS_NAME, const.SUPERCIAS_PDF_UI_WIDGET_OVERLAY))
                                )
                                
                        except TimeoutException:
                            print("El visor de PDF no apareció. Es posible que el clic no funcionara.")
                        
                        time.sleep(3) 
                        
                    except Exception as e:
                        print(f"Error con PDF {id_pdf}: {e}")
                        # Resetear el estado para el siguiente PDF
                        self._driver.switch_to.default_content()

    def check_modal_firma_electronica(self):
        main_window = None
        try:
            # 1. Guardar la ventana principal ANTES de cualquier interacción
            main_window = self._driver.current_window_handle
            
            # Timeout corto: si no está, no es un PDF con firmas
            wait = WebDriverWait(self._driver, 4)
            boton_aceptar = wait.until(EC.element_to_be_clickable((By.XPATH, const.SUPERCIAS_XPATH_BUTTON_SIGN)))
            
            print("Modal de Firmas detectado. Procesando...")

            # 2. Hacer el clic
            boton_aceptar.click()

            # 3. ESPERA CRUCIAL: Esperar a que aparezca la nueva ventana
            # Si el clic cierra la principal o abre una nueva, aquí lo capturamos
            wait.until(lambda d: len(d.window_handles) > 1)
            
            # 4. Identificar la nueva ventana
            new_window = [h for h in self._driver.window_handles if h != main_window][0]
            
            # Cambiar a la nueva ventana (donde está el PDF)
            self._driver.switch_to.window(new_window)
            
            print(f"Descargando desde nueva ventana: {self._driver.current_url}")
            time.sleep(3) # Tiempo para que inicie la descarga
            
            # 5. CERRAR la ventana del PDF y VOLVER
            self._driver.close()
            self._driver.switch_to.window(main_window)

        except TimeoutException:
            print("No se detectó modal de firmas, continuando flujo estándar.")
        except Exception as e:
            print(f"Error manejando firmas: {e}")
            # RECOPERACIÓN DE EMERGENCIA:
            # Si la ventana actual se cerró, intentamos rescatar la principal
            try:
                if len(self._driver.window_handles) > 0:
                    self._driver.switch_to.window(self._driver.window_handles[0])
            except:
                pass

    def exist_dialog_captcha(self):
        try:
            # 1. Esperar a que el contenedor principal sea VISIBLE (no solo que exista)
            # Usamos un selector que combine el ID y que NO tenga el estilo hidden
            wait = WebDriverWait(self._driver, 3) 
            
            # Este selector es más agresivo: busca el div que esté visible
            captcha_visible = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, const.SUPERCIAS_CSS_SELECTOR_DIALOG_CAPTCHA_DISPLAY)
            ))
            
            # 2. Verificar que la imagen del captcha ya tenga una URL cargada
            # A veces el diálogo abre pero la imagen está en blanco un segundo
            imagen = self._driver.find_element(By.ID, const.SUPERCIAS_DIALOG_IMAGE_CAPTCHA)
            if imagen.get_attribute("src"):
                return True
                
            return False
        except TimeoutException:
            return False
                
    def resolve_dialog_captcha(self):
        wait = WebDriverWait(self._driver, 120)
        image_base64 = self.get_image_captcha_base64_to_login(const.SUPERCIAS_DIALOG_IMAGE_CAPTCHA)
        code = self.resolve_captcha(image_base64=image_base64)

        if not code:
            print("No se pudo obtener el código")
        
        input_captcha = wait.until(EC.presence_of_element_located((By.ID, const.SUPERCIAS_DIALOG_INPUT_CAPTCHA)))
        if not input_captcha:
            print('No se econtro aun el input del captcha')
            return
        input_captcha.clear()
        input_captcha.send_keys(code)

        button_search = self._driver.find_element(By.ID, const.SUPERCIAS_DIALOG_VERIFY_CAPTCHA)
        button_search.click()

        # --- BLOQUE DE SEGURIDAD POST-RESOLUCIÓN ---
        print("Captcha enviado, limpiando interfaz...")
        
        # 1. Esperar a que el diálogo del captcha desaparezca de la vista
        wait.until(EC.invisibility_of_element_located((By.ID, "dlgCaptcha")))
        time.sleep(1)



