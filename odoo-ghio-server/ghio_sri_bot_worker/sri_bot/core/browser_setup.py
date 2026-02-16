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

from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from ..config import settings
import os
import json
from dotenv import load_dotenv
from selenium_stealth import stealth

load_dotenv()

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
        options = Options()
        #options = uc.ChromeOptions()
        for option in settings.BROWSER_OPTIONS:
            options.add_argument(option)

        
        # options.add_argument("--disable-gpu")  # Desactivar GPU
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-software-rasterizer")

        # extension_path = r"C:\Users\ALEJANDRO-PC\Desktop\GAHEOS-PROJECTS\ilga_scraping\extension"

        # options.add_argument(f"--load-extension={extension_path}")

        #options.add_argument(r"load-extension=C:\\Users\\ALEJANDRO-PC\\Desktop\\GAHEOS-PROJECTS\\ilga_scraping\\extension")

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
        #driver = uc.Chrome(options=options, stop_proc_on_exit=False)
        #driver = webdriver.Chrome(options=options)
        driver.__class__ = ChromeWebDriver
        # Extraer versión real del binario ejecutado
        # real_version = driver.capabilities['browserVersion']
        # actual_user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{real_version} Safari/537.36"
        user_agent_real = driver.execute_script("return navigator.userAgent")
        # 3. Aplicar Selenium-Stealth
        # Esto modifica el objeto 'navigator' y otros parámetros de hardware
        stealth(driver,
            user_agent=user_agent_real,
            languages=["es-EC", "es"],
            vendor="Google Inc.",
            platform="Win32", # Simula que estás en Windows aunque el Grid esté en Linux/Docker
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            fix_canvas=True
        )


        return driver
