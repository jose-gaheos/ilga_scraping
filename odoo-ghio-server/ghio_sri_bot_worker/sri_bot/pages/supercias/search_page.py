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


class SearchPage(BasePage):
    def __init__(self, manager, identification, solver=None, extra_ci=None):
        super().__init__(manager)
        self._identification = identification
        self._extra_ci = extra_ci
        self._solver = manager.solver
        self._headers_image = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def run(self):
        if not self.ensure_action(const.ACTION_SUPERCIA_SEARCH, const.STATE_INITIAL):
            print("Action or state not valid for SearchPage")
            return False

        self.action = const.ACTION_LOGIN, const.STATE_PENDING

        if element := self.wait_for_element_visible(const.SUPERCIAS_XPATH_SEARCH_FORM):
            self.move(element)
            self.click(element)
            self.wait(const.AWAIT_OPEN)
        else:
            self.state = const.STATE_ERROR
            return False

        if not self.is_safe:
            return False

        self.state = const.STATE_READY

        if radio_field := self.wait_for_element(const.SUPERCIAS_XPATH_RADIO_RUC, by=By.CSS_SELECTOR, timeout=const.TIMEOUT_MINIMUM):
            self.move(radio_field)
            self.click(radio_field)
        else:
            self.error('RUC radio field not found')
            self.state = const.STATE_INVALID
            return False

        print('identification: ', self._identification )
        if self._identification:
            if input_field := self.wait_for_element(const.SUPERCIAS_INPUT_RUC, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
                self.click(input_field)
                self.send_keys(input_field, self._identification)
            else:
                self.error('Identification input field not found')
                self.state = const.STATE_INVALID
                return False

        if first_result := self.wait_for_element(const.SUPERCIAS_XPATH_FIRST_RESULT_RUC, timeout=const.TIMEOUT_MEDIUM):
            self.click(first_result)
        else:
            self.error('First result not found')
            self.state = const.STATE_INVALID
            return False

        try:
            # Cambiar estado antes de resolver captcha
            self.action = const.ACTION_SUPERCIA_RECAPTCHA
            self.state = const.STATE_READY

            if input_captcha := self.wait_for_element(const.SUPERCIAS_INPUT_CAPTCHA_LOGIN, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
                if image_captcha_base64 := self.get_image_captcha_base64_to_login(const.SUPERCIAS_IMAGE_CAPTCHA_LOGIN):
                    captcha_solution = self.solve_captcha_image(image=image_captcha_base64)
                    if not captcha_solution:
                        self.state = const.STATE_ERROR
                        return False
                    self.send_keys(input_captcha, captcha_solution)
                else:
                    self.error('Captcha image not found')
                    self.state = const.STATE_INVALID
                    return False
        except Exception as e:
            self.error(f'Captcha handling error image captcha: {e}')
            self.state = const.STATE_ERROR
            return False
        
        if not self.ensure_action(const.ACTION_SUPERCIA_RECAPTCHA, const.STATE_SUCCESS):
            print("Action or state not valid before clicking search button")
            return False
            
        if button_login := self.wait_for_element(const.SUPERCIAS_BUTTON_SEARCH_LOGIN, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            self.click(button_login)
        else:
            self.error('Button search not found')
            self.state = const.STATE_INVALID
            return False

        self.wait(const.AWAIT_OPEN)

        if not self.is_safe:
            return False

        if not self.wait_for_element(const.SUPERCIAS_MAIN_MENU, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            self.state = const.STATE_ERROR
            return False
        
        if self.ensure_action(const.ACTION_SUPERCIA_RECAPTCHA, const.STATE_SUCCESS):
            self.info(f"Authenticated User: {self._identification}")
            self.action = const.ACTION_HOME_SUPERCIAS
            self.state = const.STATE_INITIAL
            return True


        self.error("Authentication failed")
        self.state = const.STATE_FAILED
        return False
    
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

        if not self._solver:
            self.error("Recaptcha solver not found")
            self.state = const.STATE_INVALID
            return None

        try:
            result = self._solver.normal(image)
            if recaptcha_code := result.get('code'):
                self.info(f'Recaptcha Solved: {recaptcha_code}')
                self.state = const.STATE_SUCCESS
                return recaptcha_code
        except Exception as e:
            self.error(f"Recaptcha solving error: {e}")
            self.state = const.STATE_ERROR
            return None
 
        
    def get_image_captcha_base64_to_login(self, query_selector):
        if image_captcha := self.wait_for_element(query_selector, by=By.ID, timeout=const.TIMEOUT_MINIMUM):
            url_image = image_captcha.get_attribute("src")
            self.info(f"Captcha image URL: {url_image}")
            return self._download_image_to_base64(url_image=url_image)
        else:
            self.error('Identification input field not found')
            self.state = const.STATE_INVALID
            return None
        
    def _download_image_to_base64(self, url_image):
        try:
            response = requests.get(url_image, headers=self._headers_image, timeout=10)
            
            if response.status_code == 200:
                # 3. Convertir los bytes de la imagen a Base64
                return base64.b64encode(response.content).decode('utf-8')
            else:
                self.error(f"No se pudo descargar la imagen. Status: {response.status_code}")
                return None
        except Exception as e:
            self.error(f"Error: {e}")
            return None