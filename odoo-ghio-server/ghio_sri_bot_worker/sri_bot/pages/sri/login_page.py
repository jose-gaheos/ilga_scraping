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

class LoginPage(BasePage):
    def __init__(self, manager, username, password, solver=None, extra_ci=None):
        super().__init__(manager)
        self._username = username
        self._password = password
        self._extra_ci = extra_ci
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # self._data = data
    

    def run(self):
        if not self.ensure_action(const.ACTION_LOGIN, const.STATE_INITIAL):
            print("Action or state not valid for SearchPage Juditial Function")
            return False

        self.action = const.ACTION_LOGIN, const.STATE_PENDING

        self.wait(const.AWAIT_OPEN)
        
        if input_field := self.wait_for_element(const.SRI_ID_INPUT_USERNAME, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            self.move(input_field)
            self.click(input_field)
            self.send_keys(input_field, self._username)
            # escribir_con_error_humano(elemento= input_field, texto = self._username, error_delete=-2)
        else:
            self.error('RUC input field not found')
            self.state = const.STATE_INVALID
            return False

        self.wait(const.AWAIT_OPEN)

        if input_field := self.wait_for_element(const.SRI_ID_INPUT_PASSWORD, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            self.move(input_field)
            self.click(input_field)
            self.send_keys(input_field, self._password)
            # escribir_con_error_humano(elemento= input_field, texto = self._password, error_delete=-3)
        else:
            self.error('Password input field not found')
            self.state = const.STATE_INVALID
            return False

        if button_login := self.wait_for_element(const.SRI_XPATH_BUTTON_LOGIN, timeout=const.TIMEOUT_MINIMUM):
            self.move(button_login)
            self.wait(const.AWAIT_MEDIUM)
            self.click(button_login)
        else:
            self.error('Login button not found')
            self.state = const.STATE_INVALID
            return False
        
        if self.wait_for_element_visible(const.SRI_TAG_PROFILE, by=By.TAG_NAME, timeout=const.TIMEOUT_LONG):
            self.info("Login successful - Profile tag found")
            # self.state = const.STATE_SUCCESS
            self.state = const.ACTION_HOME, const.STATE_INITIAL
            return True
        

        self.error("Authentication failed")
        self.state = const.STATE_FAILED
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
