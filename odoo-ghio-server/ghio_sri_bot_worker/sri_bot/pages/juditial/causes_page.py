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

class CausesPage(BasePage):
    def __init__(self, manager, data, solver=None, extra_ci=None):
        super().__init__(manager)
        self._data = data
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    

    def run(self):
        if not self.ensure_action(const.ACTION_HOME, const.STATE_INITIAL):
            print("Action or state not valid for CausesPage Juditial Function")
            return False

        self.action = const.ACTION_HOME, const.STATE_PENDING

        if causes := self.find_elements(const.JF_CLASS_LIST_CAUSES, by=By.CLASS_NAME):
            self.action = const.ACTION_HOME, const.STATE_READY
            if list_causes := self.get_list_causes(list_causes=causes):
                self._data['causes'] = list_causes
                self.info(f"Causes found: {json.dumps(list_causes)}")
                self.action = const.ACTION_HOME, const.STATE_SUCCESS

            return True
        
        # if self.ensure_action(const.ACTION_HOME, const.STATE_SUCCESS):
        #     print("Action or state not valid after waiting for causes list")
        #     return False

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