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

from .base_page import BasePage
from ..config import const


class DocumentsPage(BasePage):
    def __init__(self, manager, worker, solver):
        super().__init__(manager)

        self.worker = worker.sudo()
        self.env = worker.env
        self._solver = solver

    def run(self):
        success = True

        if not self.ensure_action(const.ACTION_LOGIN):
            return False

        for task in self.worker.stage_ids:
            self.open(const.DOCUMENTS_URL)

            if not self.is_safe:
                return False

            self.action = const.ACTION_DOCUMENTS, const.STATE_PENDING

            if self.wait_for_element(const.DOCUMENTS_XPATH_TEST):
                self.state = const.STATE_READY
            else:
                return self.error("Documents form not found")

            if not self.form_select(const.DOCUMENTS_FORM_XPATH_YEAR, task.year):
                self.error('Year select field not found')
                self.state = const.STATE_INVALID
                return False

            if not self.form_select(const.DOCUMENTS_FORM_XPATH_MONTH, task.month):
                self.error('Month select field not found')
                self.state = const.STATE_INVALID
                return False

            if not self.form_select(const.DOCUMENTS_FORM_XPATH_DAY, task.day):
                self.error('Day select field not found')
                self.state = const.STATE_INVALID
                return False

            if not self.form_select(const.DOCUMENTS_FORM_XPATH_DOCUMENT_TYPE, task.document_type):
                self.error('Document type select field not found')
                self.state = const.STATE_INVALID
                return False

            if self._run(task):
                task.state = 'done'
            else:
                task.state = 'error'
                success = False

            self.env.cr.commit()

        return success

    def _run(self, task):
        self.state = const.STATE_PENDING

        self.state = const.STATE_READY

        if recaptcha_code := self.recaptcha_solve() and self.ensure_action(const.ACTION_DOCUMENTS_RECAPTCHA):
            self.driver.execute_script(f'rcBuscar("{recaptcha_code}")')
        else:
            return False

        self.action = const.ACTION_DOCUMENTS, const.STATE_READY

        self.wait(const.AWAIT_OPEN)

        if self.wait_for_element(const.DOCUMENTS_FORM_XPATH_TABLE, by=By.ID):
            self.state = const.STATE_SUCCESS
            return self.download(task)

        if (warn := self.wait_for_element(
                const.DOCUMENTS_FORM_XPATH_WARNING)) and const.DOCUMENTS_FORM_XPATH_WARNING_MSG in warn.text:
            self.warn('No documents found')
            self.state = const.STATE_FAILED
            return True

        return False

    def recaptcha_solve(self):
        for i in range(const.RETRY_TIMES_MINIMUM):
            if recaptcha_code := self._recaptcha_solve():
                return recaptcha_code
            self.error(f"Recaptcha solving attempt {i + 1} failed")
            self.wait(const.AWAIT_MEDIUM)
        return None

    def _recaptcha_solve(self):
        if not (self.ensure_action(const.ACTION_DOCUMENTS, const.STATE_READY) or
                self.ensure_action(const.ACTION_DOCUMENTS_RECAPTCHA, const.STATE_ERROR)):
            return None

        self.action = const.ACTION_DOCUMENTS_RECAPTCHA, const.STATE_PENDING

        if not self._solver:
            self.error("Recaptcha solver not found")
            self.state = const.STATE_INVALID
            return None

        if recaptcha_response := self.wait_for_element(const.DOCUMENTS_RECAPTCHA_XPATH_RESPONSE, By.ID):
            site_key = None
            if g_recaptcha := self.wait_for_element(const.DOCUMENTS_RECAPTCHA_XPATH_CONTAINER, By.CLASS_NAME):
                site_key = g_recaptcha.get_attribute(const.DOCUMENTS_RECAPTCHA_XPATH_ATTRIBUTE)

            if site_key:
                self.info(f"Recaptcha site key: {site_key}")
                self.state = const.STATE_READY
            else:
                self.error("Recaptcha container not found")
                self.state = const.STATE_INVALID
                return None

            try:
                result = self._solver.recaptcha(sitekey=site_key, url=self.driver.current_url)
                if recaptcha_code := result.get('code'):
                    self.driver.execute_script(f'arguments[0].value = "{recaptcha_code}";', recaptcha_response)
                    self.info('Recaptcha Solved')
                    self.state = const.STATE_SUCCESS
                    return recaptcha_code
            except Exception as e:
                self.error(f"Recaptcha solving error: {e}")
                self.state = const.STATE_ERROR
                return None
        else:
            self.error("Recaptcha response not found")
            self.state = const.STATE_INVALID
            return None

    def get_pages(self):
        if pages := self.wait_for_element(const.DOCUMENTS_TABLE_XPATH_PAGES):
            for fp, lp in re.findall(r'(\d+) .* (\d+)', pages.text):
                return [int(fp), int(lp)]
        else:
            self.error('Documents table not found')
            self.state = const.STATE_INVALID
        return None

    def download(self, task):
        download_path = self.manager._ensure_download_path(task.year, task.month)

        current_page = last_page = 1
        if pages := self.get_pages():
            last_page = pages[1]

        if last_page > 1:
            if table := self.wait_for_element(const.DOCUMENTS_TABLE_XPATH_DATA, by=By.ID):
                if not self._click_last(table):
                    return False

                current_page = last_page

        while current_page >= 1:
            self.info(f"Processing page {current_page}")
            ensured = False
            if table := self.wait_for_element(const.DOCUMENTS_TABLE_XPATH_DATA, by=By.ID):
                access_keys = []
                files_to_sync = []
                index_min = None

                if rows := self.find_elements(const.DOCUMENTS_TABLE_XPATH_ROW, parent=table):
                    self.info(f"Documents found: {len(rows)}")
                    for row in rows:
                        if access_key_element := self.find_element('.//td[4]', parent=row):
                            access_key = access_key_element.text
                            index = int(row.get_attribute('data-ri'))
                            if index_min is None:
                                index_min = index
                            index_min = min(index_min, index)
                            if not access_key:
                                continue

                            if date_element := self.find_element('.//td[6]', parent=row):
                                row_date = (date_element.text or '').strip()
                                if not row_date:
                                    continue
                                row_date = datetime.datetime.strptime(row_date, '%d/%m/%Y').date()
                                if task.date_from > row_date:
                                    current_page = 0
                                    continue
                                if task.date_to < row_date:
                                    continue

                            access_keys.append((access_key, index))

                    for access_key, index, skip in self.worker._filter_access_keys(access_keys):
                        if skip:
                            self.info(f"SKIP {access_key}")
                        else:
                            file_data = {}

                            if not ensured:
                                if el := self.wait_for_element(const.DOCUMENTS_DOWNLOAD_PARAM_XML % index, by=By.ID):
                                    ensured = self.click_js(el, wait=const.AWAIT_MEDIUM)

                            if file_path := self._download(task, access_key, index, 'xml', download_path):
                                file_data['path_xml'] = file_path

                            if file_path := self._download(task, access_key, index, 'pdf', download_path):
                                file_data['path_pdf'] = file_path

                            if file_data:
                                file_data.update({
                                    'name': access_key,
                                    'process_id': self.worker.id,
                                })
                                files_to_sync.append(file_data)

                    if files_to_sync:
                        self.env['ghio.sri_bot.worker.file'].create(files_to_sync)
                        self.env.cr.commit()
                else:
                    self.warn('No documents found')

                if current_page > 1:
                    if not self._click_prev(index_min, table):
                        return False
                    self.wait(const.AWAIT_MEDIUM)

            else:
                self.error('Documents table not found')
                self.state = const.STATE_INVALID
                return False

            current_page -= 1
        return True

    def _click_next(self, index, parent):
        return self._click_page(index + 1, parent, const.DOCUMENTS_TABLE_XPATH_NEXT_PAGE)

    def _click_prev(self, index, parent):
        return self._click_page(index - 1, parent, const.DOCUMENTS_TABLE_XPATH_PREV_PAGE)

    def _click_last(self, parent):
        if go_page := self.wait_for_element(const.DOCUMENTS_TABLE_XPATH_LAST_PAGE):
            self.click_js(go_page)

        if self.wait_for_element(const.DOCUMENTS_TABLE_XPATH_ROW, parent=parent):
            for _i in range(const.RETRY_TIMES_MAXIMUM):
                if not self.find_element(const.DOCUMENTS_TABLE_XPATH_ROW_INDEX % 0, parent=parent):
                    return True
                self.wait(const.AWAIT_MEDIUM)
        return False

    def _click_page(self, index, parent, selector):
        if go_page := self.wait_for_element(selector):
            self.click_js(go_page)

            if self.wait_for_element(
                    const.DOCUMENTS_TABLE_XPATH_ROW_INDEX % index,
                    parent=parent,
                    timeout=const.TIMEOUT_MAXIMUM
            ):
                return True
        return False

    def _download(self, task, access_key, index, file_type, download_path):
        success = False
        filename = f'{access_key}.{file_type}'
        file_path = os.path.join(download_path, filename)
        try:
            response = self._download_perform_request(task, index, const.DOCUMENTS_DOWNLOAD_PARAM[file_type])
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    file.write(response.content)
                self.info(f"Downloaded: {filename}")
                success = True
            else:
                self.error(f"Download error: {response.status_code}")
        except Exception as e:
            self.error(f"Download error: {e}")
        self.wait(const.AWAIT_DOWNLOAD)
        if not success:
            return None
        return file_path

    def _download_prepare_headers(self):
        return dict(
            **const.DOCUMENTS_DOWNLOAD_HEADER,
            **{
                'Accept-Language': self.driver.execute_script("return navigator.language || navigator.userLanguage;"),
                'Origin': self.driver.current_url,
                'Referer': self.driver.current_url,
                'User-Agent': self.driver.execute_script("return navigator.userAgent;"),
                'sec-ch-ua': self.driver.execute_script(
                    "return navigator.userAgentData.brands.map(b => `${b.brand};v=${b.version}`).join(', ');"),
                'sec-ch-ua-platform': self.driver.execute_script("return navigator.userAgentData.platform;")
            }
        )

    def _download_prepare_cookies(self):
        return {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}

    def _download_perform_request(self, task, index, param):
        return requests.post(
            const.DOCUMENTS_DOWNLOAD_URL,
            headers=self._download_prepare_headers(),
            cookies=self._download_prepare_cookies(),
            data={
                'frmPrincipal': 'frmPrincipal',
                'frmPrincipal:opciones': 'ruc',
                'frmPrincipal:ano': task.year,
                'frmPrincipal:mes': task.month,
                'frmPrincipal:dia': task.day,
                'frmPrincipal:cmbTipoComprobante': task.document_type,
                'g-recaptcha-response': '',
                'javax.faces.ViewState': self.driver.find_element(By.NAME, "javax.faces.ViewState").get_attribute(
                    "value"),
                param % index: param % index
            }
        )
