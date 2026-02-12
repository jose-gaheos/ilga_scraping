#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################
import datetime
import os
import re
import time

import requests
from selenium.webdriver.common.by import By

from ..base_page import BasePage
from ...config import const


class DocumentsPage(BasePage):
    def __init__(self, manager, solver):
        super().__init__(manager)

        self._solver = solver

    def run(self):
        success = True

        if not self.ensure_action(const.ACTION_LOGIN):
            return False

       

        return success