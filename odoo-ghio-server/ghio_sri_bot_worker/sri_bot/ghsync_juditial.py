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
import time

from logging import getLogger
from selenium.webdriver import ActionChains
from twocaptcha import TwoCaptcha

from .core.browser_setup import BrowserSetup
from .config import settings, const
from . import pages
from .pages.juditial import SearchPage, CausesPage
import json

_logger = getLogger(__name__)


class GHSyncJuditial:
    def __init__(
            self,
            uid,
            identification,
            nombre = None,
            selenium_url='http://localhost:4446/wd/hub',
            home_path='/tmp/files',
            solver_apikey=None,
            logs_tracking='error',
            username = None,
            password = None,
            extra_ci = None
    ):
        # Project UID
        self._uid = uid

        # Selenium URL
        self._selenium_url = selenium_url

        # Supercia credentials
        self._identification = identification
        self._nombre = nombre

        # Paths
        self._home_path = os.path.join(home_path, 'funcion_judicial')
        self._downloads_path = os.path.join(self._home_path, 'downloads')
        self._profile_path = os.path.join(self._home_path, 'profile')
        self._logs_path = os.path.join(self._home_path, 'logs')
        self._ensure_paths()

        # Logs
        self._logs = []
        self._logs_tracking = settings.LOG_TRACKING.get(logs_tracking, ())
        self._logger = _logger

        # State
        self._action = const.ACTION_LOGIN
        self._state = const.STATE_INITIAL

        # Selenium
        self._driver = None
        self._driver_actions = None
        self.driver = BrowserSetup(
            self._selenium_url,
            self._profile_path,
            self._downloads_path,
        ).setup()

        # 2Captcha
        self.solver = TwoCaptcha(solver_apikey) if solver_apikey else None

        self._data = {}

        self._url = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"

        # Start
        # self.state = const.STATE_READY

    @property
    def uid(self):
        return self._uid

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value
        if value:
            self._driver_actions = ActionChains(value)
        self.info("Driver set")

    @property
    def driver_actions(self):
        return self._driver_actions

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if isinstance(value, (list, tuple)):
            self._set_action(*value)
        else:
            self._set_action(self._action, value)

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if isinstance(value, (list, tuple)):
            self._set_action(*value)
        else:
            self._set_action(value, self._state)

    @property
    def errors(self):
        return [log for log in self._logs if log['type'] == 'error']

    @property
    def warnings(self):
        return [log for log in self._logs if log['type'] == 'warning']

    @property
    def logs(self):
        return list(self._logs)

    @property
    def logger(self):
        return self._logger

    def ensure_action(self, action, state=const.STATE_SUCCESS):
        if self.action != action or self.state != state:
            return False
        return True

    def error(self, message):
        self.log(message, log_type='error')
        return False

    def warn(self, message):
        self.log(message, log_type='warning')
        return True

    def info(self, message):
        self.log(message, log_type='info')
        return True

    def log(self, message, log_type='info'):
        log = {
            'message': message,
            'timestamp': datetime.datetime.now(),
            'type': log_type,
            'uid': self._uid,
            'state': self.state,
            'action': self.action,
            'url': self._driver.current_url if self.state not in (
                const.STATE_INITIAL, const.STATE_CLOSED) and self._driver else None
        }
        log_message = f"[{log['uid']}][{log['action']}/{log['state']}]: {log['message']}"
        if log_type in self._logs_tracking:
            self._logs.append(log)
        if log_type == 'error':
            self.logger.error(log_message)
        elif log_type == 'warning':
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def download(self, worker):
        res = self.run_pages(worker)
        self._clean_download_path()
        self.close()
        return res

    def test_auth(self):
        res = self.run_auth()
        self.close()
        return res

    def run(self):
        self.driver.get(self._url)
        if not SearchPage(self, self._nombre, self._data).run():
            return False
        if not CausesPage(self, self._data, self._downloads_path).run():
            return False
        print('Data: :',json.dumps(self._data, indent=4, ensure_ascii=False))
        return True

    def run_pages(self, worker):
        if not pages.HomePage(self).run():
            return False
        if not pages.LoginPage(self, self._username, self._password, self._extra_ci).run():
            return False
        if not pages.DocumentsPage(self, worker, self.solver).run():
            return False

    def close(self):
        self.state = const.STATE_CLOSED
        self.driver.quit()
        self.driver = None
        self.log("Browser closed")

    def keep_alive(self):
        self.driver.execute_script("window.scrollBy(0, 10);")

    wait = time.sleep

    def _set_action(self, action, state):
        action_changed = state_changed = False
        if self.action != action:
            self._action = action
            action_changed = True
        if self.state != state:
            self._state = state
            state_changed = True
        if action_changed and state_changed:
            self.info(f'Action changed to: {action}, State changed to: {state}')
        elif action_changed:
            self.info(f'Action changed to: {action}')
        elif state_changed:
            self.info(f'State changed to: {state}')

    def _ensure_paths(self):
        for directory in [
            self._home_path,
            self._downloads_path,
            self._profile_path,
            self._logs_path
        ]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def _clean_download_path(self):
        for file in os.listdir(self._downloads_path):
            if os.path.isfile(os.path.join(self._downloads_path, file)) and file.endswith('.xml'):
                os.remove(os.path.join(self._downloads_path, file))

    def _ensure_download_path(self, year, month):
        download_directory = os.path.join(self._downloads_path, f'{year}_{month}')
        if not os.path.exists(download_directory):
            os.makedirs(download_directory)
        return download_directory

    def _ensure_sent_path(self, year, month):
        process_directory = os.path.join(self._ensure_download_path(year, month), 'sent')
        if not os.path.exists(process_directory):
            os.makedirs(process_directory)
        return process_directory
