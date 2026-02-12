#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

import time
import random

from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ..config import settings, const
from ..core.ghsync_base import GHSyncBase


class BasePage(GHSyncBase):
    @property
    def driver(self):
        return self.manager.driver

    @property
    def driver_actions(self):
        return self.manager.driver_actions

    @property
    def solver(self):
        return self.manager.solver

    @property
    def is_safe(self):
        if body := self.wait_for_element('//body', mute=True, timeout=const.TIMEOUT_SHORT):
            try:
                children = body.find_elements(By.XPATH, './*')
                if not children or (len(children) == 1 and children[0].tag_name == 'table'):
                    self.state = const.STATE_PAGE_ERROR
                    return False
            except Exception:
                pass
        return True

    def open(self, url, wait=const.AWAIT_OPEN):
        try:
            self.info(f"Opening URL: {url}")
            self.driver.get(url)
            self.wait(wait)
            if self.is_safe:
                self.info(f"Opened URL: {url}")
                return True
        except Exception as e:
            return self.error(f"Error opening URL: {url}, {e}")
        return False

    def click(self, element, wait=const.AWAIT_CLICK):
        try:
            element.click()
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Clicking error: {e}")
            return False

    def click_js(self, element, wait=const.AWAIT_CLICK):
        try:
            self.driver.execute_script("arguments[0].click();", element)
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Clicking error: {e}")
            return False
        
    def scroll(self, element, wait=const.AWAIT_CLICK):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Scrolling error: {e}")
            return False
        

    def open_new_tab(self, element, wait=const.AWAIT_CLICK):
        try:
            self.driver.execute_script("arguments[0].setAttribute('target', '_blank');", element)
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Scrolling error: {e}")
            return False

    def move(self, element, wait=const.AWAIT_MOVE):
        try:
            self.driver_actions.move_by_offset(random.randint(10, 100), random.randint(10, 100)).perform()
            time.sleep(random.uniform(0.5, 1.5))
            self.driver_actions.move_to_element(element).perform()
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Move to element error: {e}")
            return False

    def send_keys(self, element, keys, wait=const.AWAIT_KEYS):
        try:
            element.send_keys(keys)
            if wait:
                self.wait(wait)
            return True
        except Exception as e:
            self.error(f"Sending keys error: {e}")
            return False

    def wait_for_element(self, selector, by=By.XPATH, timeout=const.AWAIT_LOCATE, mute=False, parent=None):
        if not parent:
            parent = self.driver
        try:
            if not mute:
                self.info(f"Waiting for element: {selector}")
            element = WebDriverWait(parent, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            if not mute:
                self.info(f"Element found: {selector}")
            return element
        except Exception as e:
            self.warn(f"Error waiting for element: {selector}, {e}")
            return None

    def find_element(self, selector, by=By.XPATH, parent=None):
        if not parent:
            parent = self.driver
        try:
            return parent.find_element(by, selector)
        except Exception as e:
            self.warn(f"Error finding element: {selector}, {e}")
            return None

    def find_elements(self, selector, by=By.XPATH, parent=None):
        if not parent:
            parent = self.driver
        try:
            return parent.find_elements(by, selector)
        except Exception as e:
            self.warn(f"Error finding elements: {selector}, {e}")
            return None

    def wait_for_element_visible(self, selector, by=By.XPATH, timeout=const.AWAIT_LOCATE, mute=False):
        try:
            self.info(f"Waiting for element to be visible: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            if not mute:
                self.info(f"Element visible found: {selector}")
            return element
        except Exception as e:
            self.error(f"Error waiting for element to be visible: {selector}, {e}")
            return None
        
    def wait_for_element_invisible(self, selector, by=By.XPATH, timeout=const.AWAIT_LOCATE, mute=False):
        try:
            self.info(f"Waiting for element to be invisible: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((by, selector))
            )
            if not mute:
                self.info(f"Element invisible found: {selector}")
            return element
        except Exception as e:
            self.error(f"Error waiting for element to be invisible: {selector}, {e}")
            return None


    def wait_for_element_clickable(self, selector, by=By.XPATH, timeout=const.AWAIT_LOCATE, mute=False):
        try:
            self.info(f"Waiting for element to be clickable: {selector}")
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            if not mute:
                self.info(f"Element clickable found: {selector}")
            return element
        except Exception as e:
            self.error(f"Error waiting for element to be clickable: {selector}, {e}")
            return None

    def form_select(self, selector, value, by=By.XPATH, timeout=const.TIMEOUT_SHORT):
        if element := self.wait_for_element_visible(selector, by=by, timeout=timeout):
            try:
                select_field = Select(element)
                select_field.select_by_value(value)
                self.wait(const.AWAIT_KEYS)
                return True
            except Exception as e:
                self.error(f"Select field error: {e}")
        return False
