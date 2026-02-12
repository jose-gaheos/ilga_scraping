#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..config import settings
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Configuración para guardado automático de PDF
# settings_save_pdf = {
#     "recentDestinations": [{
#         "id": "Save as PDF",
#         "origin": "local",
#         "account": ""
#     }],
#     "selectedDestinationId": "Save as PDF",
#     "version": 2
# }

# prefs = {
#     "download.default_directory": DOWNLOAD_DIR, # Cambia esto
#     "download.prompt_for_download": False,
#     "plugins.always_open_pdf_externally": True, # Forzar descarga
#     "download.directory_upgrade": True,
#     "printing.print_preview_sticky_settings.appState": json.dumps(settings),
#     "savefile.default_directory": DOWNLOAD_DIR
# }

class BrowserSetup:
    def __init__(self, selenium_url, profile_dir, downloads_dir, required_cookies = False):
        self.selenium_url = selenium_url
        self.profile_dir = profile_dir
        self.downloads_dir = downloads_dir
        self.required_cookies = required_cookies
    def setup(self):
        # options = Options()
        options = uc.ChromeOptions()
        for option in settings.BROWSER_OPTIONS:
            options.add_argument(option)

        
        # options.add_argument("--disable-gpu")  # Desactivar GPU
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("detach", True)

        # Especifica una carpeta en tu PC donde se guardará tu sesión de Google
        #options.add_argument(f"user-data-dir=/Users/josecruz/Documents/SeleniumProjects/odoo-ghio-server/cookies")
        print('self.required_cookies: ', self.required_cookies)
        if self.required_cookies:
            options.set_capability("browserName", "chrome")
            options.set_capability("ghio:node_id", "sri_persistent")

            print("!!! MODO PERSISTENTE ACTIVADO - USANDO /tmp/cookies/chrome_profile !!!")
            options.add_argument("--user-data-dir=/tmp/cookies/chrome_profile")
            options.add_argument("--profile-directory=Perfil_SRI")
            
            # AÑADE ESTO PARA DEPURAR:
            options.add_argument("--enable-logging")
            options.add_argument("--v=1")

        else:
            options.set_capability("browserName", "chrome")
            options.add_argument(f"--user-data-dir={self.profile_dir}")
            #pass
            # options.add_argument(f"--user-data-dir={self.profile_dir}")

        print("Using downloads_dir directory:", self.downloads_dir)
        
        options.add_experimental_option("prefs", {
            "download.default_directory": settings.BROWSER_PREFS.get(
                'download.default_directory') or self.downloads_dir,
            "download.prompt_for_download": settings.BROWSER_PREFS.get('download.prompt_for_download', False),
            "download.directory_upgrade": settings.BROWSER_PREFS.get('download.directory_upgrade', True),
            "safebrowsing.enabled": settings.BROWSER_PREFS.get('safebrowsing.enabled', True),
            "savefile.default_directory": settings.BROWSER_PREFS.get(
                'download.default_directory') or self.downloads_dir,
        })

        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        driver = webdriver.Remote(command_executor=self.selenium_url, options=options)
        # driver = uc.Chrome(options=options)
        # driver = webdriver.Chrome(options=options)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                // 1. Eliminar rastro de WebDriver
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

                // 2. Simular Plugins
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

                // 3. Simular Lenguajes
                Object.defineProperty(navigator, 'languages', { get: () => ['es-EC', 'es', 'en'] });

                // 4. Simular WebGL (Hardware real)
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Open Source Technology Center';
                    if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 550 (SKL GT2)';
                    return getParameter.apply(this, arguments);
                };
            """
        })
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        #     "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        #     "sec-ch-ua-mobile": "?0",
        #     "sec-ch-ua-platform": '"macOS"',
        #     "sec-fetch-dest": "document",
        #     "sec-fetch-mode": "navigate",
        #     "sec-fetch-site": "same-origin",
        #     "sec-fetch-user": "?1",
        #     # "upgrade-insecure-requests": "1"
        # }
        #
        # driver.execute_cdp_cmd('Network.enable', {})
        #
        # driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {'headers': headers})

        return driver
