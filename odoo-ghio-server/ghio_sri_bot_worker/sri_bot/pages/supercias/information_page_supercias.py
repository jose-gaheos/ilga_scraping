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
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests
import base64
import os

from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

url_server_remote = os.getenv('URL_SERVER')


class InformationSupercias(BasePage):
    def __init__(self, manager, data, downloads_path):
        super().__init__(manager)
        self._data = data
        self._downloads_path = downloads_path

    def run(self):
        if not self.ensure_action(const.ACTION_HOME_SUPERCIAS, const.STATE_INITIAL):
            return False

        self.state = const.STATE_PENDING

        if not (menu := self.wait_for_element_visible(const.SUPERCIAS_MAIN_MENU, by=By.ID, timeout=15.0)):
            self.error("Main menu not found")
            self.state = const.STATE_INVALID
            return False
        
        if not menu.is_displayed():
            self.error("Menu not displayed")
            self.state = const.STATE_INVALID
            return False
        
        self.state = const.STATE_READY
        self.move(menu)
        
        if not (accordion_element := self.wait_for_element_visible(const.SUPERCIAS_ACCORDION_GENERAL_INFORMATION, timeout=15.0)):
            self.error("Accordion element not found")
            self.state = const.STATE_INVALID
            return False

        parent_accordion_element = self.find_element(const.SUPERCIAS_PARENT_ACCORDION_GENERAL_INFORMATION, by=By.XPATH)

        general_information = self._extract_accordion_information(accordion_element=parent_accordion_element)
        current_administrators, elements_to_download_pdf = self._get_current_administrators()

        if elements_to_download_pdf:
            if not self.execute_download_pdf(elements=elements_to_download_pdf):
                self.error("Error downloading administrator PDFs")
                self.state = const.STATE_ERROR
                self.action = const.ACTION_HOME_SUPERCIAS
                return False

        # if not self.get_annual_information();

        if not self.get_annual_information() or not self.ensure_action(const.ACTION_HOME_SUPERCIAS, const.STATE_SUCCESS):
            self.state = const.STATE_ERROR
            return False

        self._data["general_information"] = general_information
        self._data["current_administrators"] = current_administrators
        return True
    
    def get_annual_information(self):

        self._verify_captcha()

        if not (menu := self.wait_for_element_visible(const.SUPERCIAS_MAIN_MENU, by=By.ID, timeout=15.0)):
            self.error("Main menu not found")
            self.state = const.STATE_INVALID
            return False
        
        self._verify_captcha()

        if not (item_annual := self.wait_for_element_clickable(const.SUPERCIAS_ITEM_ANNUAL_INFORMATION, by=By.ID)):
            self.error("Item annual not found")
            self.state = const.STATE_INVALID
            return False
        
        self.click(item_annual)
        
        self._verify_captcha()

        if not (self.wait_for_element_visible(const.SUPERCIAS_CONTAINER_TABLE_ANNUAL_INFORMATION, by=By.ID, timeout=10.0)):
            self.error("Annual Information table body not found")
            return []

        # WebDriverWait(self.driver, 10).until(
        #     lambda d: d.find_elements(By.ID, const.SUPERCIAS_CONTAINER_TABLE_ANNUAL_INFORMATION) or 
        #             d.find_elements(By.CSS_SELECTOR, const.SUPERCIAS_DIALOG_CAPTCHA)
        # )

        # 2. Ahora sí, usamos el IF con OR que querías para la lógica de negocio
 
        # Aquí decides qué camino tomar
        # if self.wait_for_element_visible(const.SUPERCIAS_DIALOG_CAPTCHA, by=By.CSS_SELECTOR):
        #     self.info("Detecté un captcha, hay que resolverlo")
        #     self._verify_captcha()
        # else:
        #     self.error("No se encontró el captcha tras esperar")
        #     # self.state = const.STATE_INVALID
        #     # return False
        self._verify_captcha()
                
            
        if not (table_header := self.wait_for_element_visible(const.SUPERCIAS_TABLE_HEADER_ANNUAL_INFORMATION, by=By.ID)):
            self.state = const.STATE_INVALID
            self.error("Table Annual Information not found")
            return False
            # input_document.send_keys("INTEGRAL")
        if not (input_document := self.find_element(const.SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT)):
            self.state = const.STATE_INVALID
            self.error("Input document not found")
            return False
        
        self.send_keys(input_document, "INTEGRAL")
        self.wait(const.AWAIT_OPEN)
        
        self._verify_captcha()

        if not (headers_table := self.find_elements(const.SUPERCIAS_XPATH_HEADER_TITLE_ANNUAL_INFORMATION)):
            self.state = const.STATE_INVALID
            self.error("Headers Estado Resultado Integral not founds")
            return False
        
        headers = [item_header.text.strip().lower() for item_header in headers_table]
        print(headers)
        
        # self.wait(const.AWAIT_OPEN)

        if not (rows_estado_resultado_integral := self.find_elements(const.SUPERCIAS_ROWS_ANNUAL_INFORMATION)):
            self.state = const.STATE_INVALID
            self.error("Filas Estado Resultado Integral not found")
            return False

      
        print('lEN: ',len(rows_estado_resultado_integral))

        self.state = const.STATE_READY

        estado_resultado_list, elements_to_download_pdf = self._extract_list_and_links_to_pdf(rows=rows_estado_resultado_integral, headers=headers)
    
        if self.ensure_action(const.ACTION_HOME_SUPERCIAS, const.STATE_ERROR):
            self.state = const.STATE_ERROR
            self.error("Error at mapped Estado Resultado Integral PDFs")
            return False
        
        if elements_to_download_pdf:
            if not self.execute_download_pdf(elements=elements_to_download_pdf[:3]):
                self.error("Error downloading Estado Resultado Integral PDFs")
                self.state = const.STATE_ERROR
                self.action = const.ACTION_HOME_SUPERCIAS
                return False
            
        if not (input_document := self.wait_for_element_clickable(const.SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT, by=By.XPATH)):
            self.state = const.STATE_INVALID
            self.error("Input document not found")
            return False
        
        input_document.clear()
        self.send_keys(input_document, "BALANCE")
        self.wait(const.AWAIT_OPEN)

        self._verify_captcha()
        
        if not (rows_balance:= self.find_elements(const.SUPERCIAS_ROWS_ANNUAL_INFORMATION)):
            self.state = const.STATE_INVALID
            self.error("Filas Estado Resultado Integral not found")
            return False
        
        balance_list, elements_to_download_pdf = self._extract_list_and_links_to_pdf(rows=rows_balance, headers=headers)
        
        if elements_to_download_pdf:
            if not self.execute_download_pdf(elements=elements_to_download_pdf[:3]):
                self.error("Error downloading Estado Resultado Integral PDFs")
                self.state = const.STATE_ERROR
                self.action = const.ACTION_HOME_SUPERCIAS
                return False
        
        if self.ensure_action(const.ACTION_HOME_SUPERCIAS, const.STATE_ERROR):
                    self.state = const.STATE_ERROR
                    self.error("Error at mapped Estado Resultado Integral PDFs")
                    return False

        self._data["estados_resultados"] = estado_resultado_list
        self._data["balances"] = balance_list

        self.state = const.STATE_SUCCESS
        return True

    def _extract_list_and_links_to_pdf(self, rows, headers):
     
        estado_resultado_list = []
        elements_to_download_pdf = []

        try:
            for row in rows[:3]:
                estados_resultados_data = {}
                cells = row.find_elements(By.TAG_NAME, const.TAG_ELEMENT_TD)
                # cells = self.find_elements(const.TAG_ELEMENT_TD, )
                print('cell lens: ', len(cells))
                for index, cell in enumerate(cells):
                    if index < len(headers):
                        estados_resultados_data[headers[index]] = cell.get_attribute("innerText").strip()

                try:
                
                    estado_resultado_name = f"{cells[0].text.strip()} {cells[2].text.strip()}"
                    if cells[-1] and (link_pdf := self.find_element(const.TAG_ELEMENT_A, By.TAG_NAME, parent=cells[-1])):
                        id_pdf = link_pdf.get_attribute("id")

                        elements_to_download_pdf.append({ 'name': estado_resultado_name, 'id_pdf': id_pdf})
                        estado_resultado_list.append(estados_resultados_data)
                except Exception as e:
                    self.info(f"Error at get info row: {e} en el index {index}")

            return estado_resultado_list, elements_to_download_pdf
        
        except Exception as e:
            self.info(f"Error extracting information pdf: {e}")
            self.state = const.STATE_ERROR


        # lista_estado_resultado, list_er_integral_pdf = self.get_annual_information_pdf(
        #     rows=rows_estado_resultado_integral,
        #     headers=headers
        # )

        # self.execute_download_pdf(elements=list_er_integral_pdf[:3])

        # time.sleep(1)
        # input_document = wait.until(EC.element_to_be_clickable((By.XPATH, const.SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT)))
        # input_document.clear()
        # input_document.send_keys("BALANCE")

        # time.sleep(3)

        # rows_balances = self._driver.find_elements(By.XPATH, const.SUPERCIAS_ROWS_ANNUAL_INFORMATION)
        # lista_balances, list_balance_pdf = self.get_annual_information_pdf(
        #     rows=rows_balances,
        #     headers=headers
        # )

        # self.execute_download_pdf(elements=list_balance_pdf[:3])
    
    def _extract_accordion_information(self, accordion_element):
        try:
            self.info(
            """Extract information from accordion element""")
            general_information = {}
            div_elements = self.find_elements(const.SUPERCIAS_XPATH_ACCORDION_INFORMATION_ITEM, parent=accordion_element)

            # if len(div_elements) == 0:
            #     self.info("No accordion items found")
            #     return general_information

            current_section = ""

            for div in div_elements:
                clase = div.get_attribute("class")
                print(f"Div class: {clase}")
                if const.SUPERCIAS_CLASS_UI_ACCORDION_HEADER in clase:
                    header_text = self._extract_section_header(div_element=div)

                    general_information[header_text] = {}
                    current_section = header_text

                if const.SUPERCIAS_CLASS_UI_ACCORDION_CONTENT in clase:
                    section_data = self._extract_section_content(div)
                    general_information[current_section] = section_data

            self.state = const.STATE_SUCCESS
            return general_information
        except Exception as e:
            self.info(f"Error extracting accordion information: {e}")
            self.state = const.STATE_ERROR
            return {}
    
    def _extract_section_header(self, div_element):
        """Extract header text from accordion section"""
        # Try configured selector first
        header = self.find_element(const.SUPERCIAS_XPATH_HEADER_ACCORDION_ITEM, parent=div_element)
        header_text = ""

        if header:
           # Probamos con textContent que es más robusto para elementos tipo acordeón
            header_text = header.get_attribute("textContent")
            
            # Si textContent falla o viene vacío, intentamos con .text
            if not header_text:
                header_text = header.text
            return header_text

        self.info(f"Header Text: {header_text}")
        return header_text
    
    def _extract_section_content(self, div_element):
        """Extract content data from accordion section"""
        section_data = {}
        rows = self.find_elements(const.SUPERCIAS_XPATH_ROWS_TBODY_CONTENT, parent=div_element)

        for item_row in rows:
            labels = self.find_elements(const.SUPERCIAS_CLASS_ROW_ITEM_CONTENT_FIRST_COLUMN, by=By.CLASS_NAME, parent=item_row)

            for label in labels:
                if cell_key := label.get_attribute("innerText").strip():
                    cell_value = self._extract_cell_value(cell_key, parent=label)
                    section_data[cell_key] = cell_value

        return section_data
    
    def _extract_cell_value(self, cell_key, parent=None):
        """Extract value from a cell element"""
        cell_value = self.find_element(const.SUPERCIAS_XPATH_CELL_VALUE_ITEM, parent=parent)
        
        if value_element := self.find_element(const.SUPERCIAS_SELECTOR_CELL_VALUE_INPUT, by=By.CSS_SELECTOR, parent=cell_value):
            value = value_element.get_attribute("value")
        else:
            value = ""

        return value.replace('\xa0', ' ').strip()
    
    def _get_current_administrators(self):
        """Extract current administrators table data"""
        administrators = []
        
        if not (menu_item := self.wait_for_element_clickable(const.SUPERCIAS_ITEM_CURRENT_ADMINISTRATORS, by=By.ID, timeout=10.0)):
            self.error("Current Administrators menu item not found")
            return administrators
        
        self._verify_captcha()

        self.click(menu_item)
        self.wait(const.AWAIT_OPEN)

        self._verify_captcha()
    
        if not (self.wait_for_element_visible(const.SUPERCIAS_TABLE_BODY_CURRENT_ADMINISTRATORS, by=By.ID, timeout=10.0)):
            self.error("Administrators table body not found")
            return administrators

        rows = self.find_elements(const.SUPERCIAS_ROWS_CURRENT_ADMINISTRATORS)

        headers = []
        header_elements = self.find_elements(const.SUPERCIAS_HEADER_CURRENT_ADMINISTRATORS)
        elements_to_download_pdf = []

        for header in header_elements:
            headers.append(header.get_attribute("innerText").strip())

        for row in rows:
            admin_data = {}
            cells = row.find_elements(By.TAG_NAME, const.TAG_ELEMENT_TD)

            for index, cell in enumerate(cells):
                if index < len(headers):
                    admin_data[headers[index]] = cell.get_attribute("innerText").strip()
            

            admin_name = f"{cells[3].text.strip()} {cells[1].text.strip()}"
            link_pdf = self.find_element( const.TAG_ELEMENT_A, By.TAG_NAME, parent=cells[-1])
            id_pdf = link_pdf.get_attribute("id")

            elements_to_download_pdf.append({ 'name': admin_name, 'id_pdf': id_pdf})
            administrators.append(admin_data)

        return administrators, elements_to_download_pdf


        
    def _verify_captcha(self):
        # wait_for_element_visible es mejor para elementos ocultos con style
        if dialog := self.find_element("dlgCaptcha", by=By.ID):
            # dialog = self.find_element("dlgCaptcha", by=By.ID)
            if dialog and dialog.is_displayed():
                self.info('Captcha dialog is visible - solving captcha')
                self.action = const.ACTION_SUPERCIA_RECAPTCHA, const.STATE_READY
                if not self._resolve_captcha_image():
                    self.state = const.STATE_ERROR
                    return False
                else:
                    self.info('Captcha dialog solved successfully')
                    self.action = const.ACTION_HOME_SUPERCIAS, const.STATE_READY
                    return True
            
        # self.state = const.STATE_INVALID
        self.state = const.STATE_READY
        # self.error('Captcha dialog expected but not visible')
        return False
       
        # self.warn('Captcha dialog not visible - may not be needed')
        # return True

    def _resolve_captcha_image(self):
        try:
            """Check and solve captcha if dialog is present"""
         
            if input_captcha := self.wait_for_element(const.SUPERCIAS_DIALOG_INPUT_CAPTCHA, by=By.ID, timeout=10.0):
                if image_captcha_base64 := self.get_image_captcha_base64_to_login(const.SUPERCIAS_DIALOG_IMAGE_CAPTCHA):
                    captcha_solution = self.solve_captcha_image(image=image_captcha_base64)
                    if not captcha_solution:
                        self.state = const.STATE_ERROR
                        return False
                    self.send_keys(input_captcha, captcha_solution)

                    if verify_button := self.wait_for_element_clickable(const.SUPERCIAS_DIALOG_VERIFY_CAPTCHA, by=By.ID, timeout=10.0):
                        self.click(verify_button)
                        self.wait(const.AWAIT_OPEN)
                        self.info("Captcha solved and submitted")
                        return True
                    else:
                        self.error("Verify captcha button not found")
                        self.state = const.STATE_ERROR
                        return False
                else:
                    self.error('Captcha image not found')
                    self.state = const.STATE_INVALID
                    return False
            return True
        except Exception as e:
            self.error(f'Captcha handling error dialog captcha: {e}')
            self.state = const.STATE_ERROR
            return False
        
    def get_image_captcha_base64_to_login(self, query_selector):
        if image_captcha := self.wait_for_element(query_selector, by=By.XPATH, timeout=const.TIMEOUT_MINIMUM):
            url_image = image_captcha.get_attribute("src")
            self.info(f"Captcha image URL: {url_image}")
            return self._download_image_to_base64(url_image=url_image)
        else:
            self.error('Identification input field not found')
            self.state = const.STATE_INVALID
            return None
        
    def _download_image_to_base64(self, url_image):
        try:
            response = requests.get(url_image, headers=self._headers_image(), timeout=10)
            
            if response.status_code == 200:
                # 3. Convertir los bytes de la imagen a Base64
                return base64.b64encode(response.content).decode('utf-8')
            else:
                self.error(f"No se pudo descargar la imagen. Status: {response.status_code}")
                return None
        except Exception as e:
            self.error(f"Error: {e}")
            return None
        
    def solve_captcha_image(self, image):
        for i in range(const.RETRY_TIMES_MINIMUM):
            if recaptcha_code := self._recaptcha_solve_image(image=image):
                return recaptcha_code
            self.error(f"Recaptcha solving attempt {i + 1} failed")
            self.wait(const.AWAIT_MEDIUM)
        return None

    def _recaptcha_solve_image(self, image):
        if not (self.ensure_action(const.ACTION_SUPERCIA_RECAPTCHA, const.STATE_READY)): 
            print("Action or state not valid for recaptcha solving")
            return None

        self.action = const.ACTION_SUPERCIA_RECAPTCHA, const.STATE_PENDING

        if not self.solver:
            self.error("Recaptcha solver not found")
            self.state = const.STATE_INVALID
            return None

        try:
            result = self.solver.normal(image)
            if recaptcha_code := result.get('code'):
                self.info(f'Recaptcha Solved: {recaptcha_code}')
                self.state = const.STATE_SUCCESS
                # self.action = const.ACTION_RECAPTCHA
                return recaptcha_code
        except Exception as e:
            self.error(f"Recaptcha solving error: {e}")
            self.state = const.STATE_ERROR
            return None

    def execute_download_pdf(self, elements):
        """Download PDFs from provided elements list"""
        document_paths = []
        if not elements or len(elements) == 0:
            self.error("No PDF elements provided for download")
            return True
        
        for item in elements:
                name = str(item.get('name')).replace(" ", "_").upper()
                id_pdf = item.get('id_pdf')
                if id_pdf:
                    try:
                        self.info(f"Iniciando descarga for {name}...")
                        # Buscamos el elemento de nuevo por ID (más seguro)
                        if button_download := self.find_element(id_pdf, By.ID):
                            button_download.click()

                            self.scroll(button_download)
                            
                        self.open_new_tab(button_download)

                        self._verify_captcha()

                        try:
                            # 3. Esperar a que el visor (object) aparezca en el DOM
                            # El selector apunta al object dentro del panel que mencionaste
                            self.info("Esperando a que el visor PDF cargue el archivo...")

                            pdf_object = self.wait_for_element(const.SUPERCIAS_PANEL_PDF_OBJECT, by=By.CSS_SELECTOR, timeout=10.0)

                            # 4. Extraer la URL del atributo 'data'
                            pdf_url_relative = pdf_object.get_attribute("data")
                            
                            if pdf_url_relative:
                                damain_url = const.SUPERCIAS_URL_DOMAIN
                                # Verificamos si la URL ya es completa o si es relativa
                                if pdf_url_relative.startswith("http"):
                                    url_completa = pdf_url_relative
                                else:
                                    # Solo concatenamos si no tiene el dominio
                                    url_completa = f"{damain_url}{pdf_url_relative}"
                                   
                                
                                self.info(f"URL corregida: {url_completa}")

                                self._verify_captcha()

                                # self.check_modal_firma_electronica()

                                file_name = f"{name}.pdf"
                                file_path = f"{url_server_remote}{self._downloads_path}/{file_name}"
                                
                                document_paths.append(file_path)
                                # 4. DESCARGA SILENCIOSA mediante JavaScript
                                # Esto evita que el navegador cambie de página o se ponga en "data:,"
                                print("Iniciando descarga silenciosa...")
                                self.driver.execute_script(f"""
                                    var link = document.createElement('a');
                                    link.href = '{url_completa}';
                                    link.download = '{file_name}';
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                """)
                                self.wait(const.AWAIT_MEDIUM)
                                # 5. CERRAR EL MODAL (Paso vital para que no estorbe al siguiente clic)
                                # Usamos JS para cerrar el modal de PrimeFaces sin buscar el botón X
                                button_close_modal = self.wait_for_element_clickable(const.SUPERCIAS_PDF_BUTTON_CLOSE, by=By.XPATH, timeout=5.0)
                                button_close_modal.click()
                               
                                # Esperar a que el bloqueo gris desaparezca
                                self.wait_for_element_invisible(const.SUPERCIAS_PDF_UI_WIDGET_OVERLAY, by=By.CLASS_NAME, timeout=5.0)

                                
                        except TimeoutException:
                            self.warn("El visor de PDF no apareció. Es posible que el clic no funcionara.")
                            return False
                        self.wait(const.AWAIT_OPEN)
                        
                    except Exception as e:
                        self.error(f"Error con PDF {id_pdf}: {e}")
                        self.state = const.STATE_ERROR
                        self.driver.switch_to.default_content()
                        return False
                        # Resetear el estado para el siguiente PDF
        
        # self._data['document_paths'] = self._data['document_paths'].extend(document_paths)
        if 'document_paths' not in self._data:
            self._data['document_paths'] = document_paths
        else:
            self._data['document_paths'].extend(document_paths)
        
        self.state = const.STATE_SUCCESS
        self.action = const.ACTION_HOME_SUPERCIAS
        return True

    def _headers_image(self):
        return  {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
                        