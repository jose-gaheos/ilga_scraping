#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

from .base_page import BasePage
from ..config import const


class LoginPage(BasePage):
    def __init__(self, manager, username, password, extra_ci=None):
        super().__init__(manager)
        self._username = username
        self._password = password
        self._extra_ci = extra_ci

    def run(self):
        if not self.ensure_action(const.ACTION_HOME):
            return False

        self.action = const.ACTION_LOGIN, const.STATE_PENDING

        if element := self.wait_for_element_visible(const.LOGIN_XPATH_LINK):
            self.move(element)
            self.click(element)
            self.wait(const.AWAIT_OPEN)
        else:
            self.state = const.STATE_ERROR
            return False

        if not self.is_safe:
            return False

        self.state = const.STATE_READY

        if input_field := self.wait_for_element(const.LOGIN_XPATH_USERNAME_INPUT, timeout=const.TIMEOUT_MINIMUM):
            self.move(input_field)
            self.click(input_field)
            self.send_keys(input_field, self._username)
        else:
            self.error('RUC input field not found')
            self.state = const.STATE_INVALID
            return False

        if self._extra_ci:
            if input_field := self.wait_for_element(const.LOGIN_XPATH_CI_INPUT, timeout=const.TIMEOUT_MINIMUM):
                self.move(input_field)
                self.click(input_field)
                self.send_keys(input_field, self._extra_ci)
            else:
                self.error('Extra CI input field not found')
                self.state = const.STATE_INVALID
                return False

        if input_field := self.wait_for_element(const.LOGIN_XPATH_PASSWORD_INPUT, timeout=const.TIMEOUT_MINIMUM):
            self.move(input_field)
            self.click(input_field)
            self.send_keys(input_field, self._password)
        else:
            self.error('Password input field not found')
            self.state = const.STATE_INVALID
            return False

        if button := self.wait_for_element(const.LOGIN_XPATH_BUTTON, timeout=const.TIMEOUT_MINIMUM):
            self.move(button)
            self.click(button)
        else:
            self.error('Login button not found')
            self.state = const.STATE_INVALID
            return False

        self.wait(const.AWAIT_OPEN)

        if not self.is_safe:
            return False

        if any(self.wait_for_element(xpath, timeout=const.TIMEOUT_MINIMUM) for xpath in const.LOGIN_XPATH_TEST):
            self.state = const.STATE_SUCCESS
            self.info(f"Authenticated User: {self._username}")
            return True

        self.error("Authentication failed")
        self.state = const.STATE_FAILED
        return False
