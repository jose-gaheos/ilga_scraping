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
import json
import os

class CausesPage(BasePage):
    def __init__(self, manager, data, downloads_path, solver=None, extra_ci=None):
        super().__init__(manager)
        self._data = data
        self._solver = manager.solver
        self._downloads_path = downloads_path
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    

    def run(self):
        if not self.ensure_action(const.ACTION_HOME, const.STATE_INITIAL):
            print("Action or state not valid for CausesPage Juditial Function")
            return False

        self.action = const.ACTION_HOME, const.STATE_PENDING

        xpath_mensaje = "//div[contains(@class, 'mat-mdc-snack-bar-label') and contains(., 'La consulta no devolvió resultados')]"

        if self.wait_for_element_visible(xpath_mensaje, by=By.XPATH, timeout=const.TIMEOUT_MINIMUM):
            self.info("No se encontraron procesos judiciales")
            self._data["causas"] = []
            self._data["message"] = "No se encontraron procesos"
            self.action = const.ACTION_HOME, const.STATE_SUCCESS
            return True

        if causes := self.find_elements(const.JF_CLASS_LIST_CAUSES, by=By.CLASS_NAME):
            self.action = const.ACTION_HOME, const.STATE_READY
            if list_causes := self.get_list_causes(list_causes=causes):
                self._data['causas'] = list_causes
                self._data['message'] = f'Se encontraron {len(list_causes)} procesos'
                self.info(f"Causes found: {json.dumps(list_causes)}")
                self.action = const.ACTION_HOME, const.STATE_SUCCESS

            return True

        self.error("Home page error")
        self.state = const.STATE_FAILED
        return False
    

    def get_list_causes(self, list_causes):
        result_causas = []
        for index, causa in enumerate(list_causes):
            try:
                cause_id = self.find_element("id", By.CLASS_NAME, parent=causa).text
                proccess_date = self.find_element("fecha", By.CLASS_NAME, parent=causa).text
                proccess_number = self.find_element("numero-proceso", By.CLASS_NAME, parent=causa).text
                action = self.find_element("accion-infraccion", By.CLASS_NAME, parent=causa).text
                file_element = self.find_element("detalle", By.CLASS_NAME, parent=causa)

                self._get_file_by_cause(element=file_element, proccess_number=proccess_number)

                data_item = {
                    "id": cause_id,
                    "number": proccess_number,
                    "date": proccess_date,
                    "action": action
                }
            except Exception as e:
                self.error(f"Error extracting data from panel {index}: {str(e)}")
                self.state = const.STATE_ERROR
                return False

            result_causas.append(data_item)
        self.info(f"Total causes extracted: {len(result_causas)}")
        return result_causas
    

    def _get_file_by_cause(self, element, proccess_number):
        try:
            if not element:
                self.error("Element not found")
                return None
            
            if link_element := self.find_element("a", by=By.TAG_NAME, parent=element):
                link_element.click()

                if cuerpo := self.wait_for_element_visible("cuerpo", by=By.CLASS_NAME):
                    if len(lista_movimientos := self.find_elements("movimiento-individual", by=By.CLASS_NAME, parent=cuerpo)) > 0:
                        first_element = lista_movimientos[0]
                        #ultimo_div = first_element.find_element(By.XPATH, "./div[last()]")
                        ultimo_div = self.find_element( "./div[last()]", by=By.XPATH, parent=first_element)
                        if link_to_page_with_pdf := self.find_element("a", by=By.TAG_NAME, parent=ultimo_div):
                            self.info("Accediendo al enlace que lleva a la pagina del pdf requerido")
                            link_to_page_with_pdf.click()
                            self.wait(const.AWAIT_OPEN)
                            if boton_pdf := self.wait_for_element_clickable( ".panel-expansion-action-buttons button:nth-child(3)", by=By.CSS_SELECTOR):
                                # Script específico para el portal de la Función Judicial
                                nombre_carpeta = f"Analisis_{proccess_number}"
                                ruta_completa = f'{self._downloads_path}/{nombre_carpeta}'
                                
                                if not os.path.exists(ruta_completa):
                                    os.makedirs(ruta_completa)
                                self.info(f"ruta_completa:  {ruta_completa}")
                                self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                                    "behavior": "allow",
                                    "downloadPath": ruta_completa
                                })
                                self.move(boton_pdf)
                                self.click(boton_pdf)

                                print(f"Descargando expediente {proccess_number} en: {nombre_carpeta}")


        except Exception as e:
            self.error(f"Error extracting file: {str(e)}")
            self.state = const.STATE_ERROR
            return False