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


class HomePage(BasePage):
    def __init__(self, manager):
        super().__init__(manager)

    def run(self):
        if not self.ensure_action(const.ACTION_SETTINGS, const.STATE_READY):
            return False

        self.action = const.ACTION_HOME, const.STATE_PENDING

        if self.open(const.HOME_URL):
            self.state = const.STATE_READY
            if element := self.wait_for_element_visible(const.HOME_XPATH_TEST, timeout=15.0):
                self.state = const.STATE_SUCCESS
                self.move(element)
                return True

        return False
