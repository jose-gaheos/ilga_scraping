#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################

BROWSER_OPTIONS = [
    # "--headless",
    #"--remote-debugging-port=9222",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
    "--disable-extensions",
    # "--disable-gpu",
    "--lang=es-EC",
    "start-maximized",
    "--disable-infobars",
    "--window-size=1920,1080",
    #"--headless=new"
]

BROWSER_PREFS = {
    "download.default_directory": None,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}

LOG_TRACKING = {
    'info': ('error', 'warning', 'info'),
    'warning': ('error', 'warning'),
    'error': ('error',)
}
