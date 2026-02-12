from selenium import webdriver
from selenium.webdriver.common.by import By
from pages.juditial_function_page_filters import JuditialFunction
import os
import time
from dotenv import load_dotenv
import json
from config import const
# Carga las variables del archivo .env
load_dotenv()

# service = webdriver.ChromeService()
def get_default_chrome_options():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-allow-origins=*")
    return options


PAGE_URL = const.JF_URL

# default_chrome_opt = get_default_chrome_options()
# driver = webdriver.Chrome(options=default_chrome_opt)

# element = driver.find_element(By.NAME, "");

def init_juditial_funciton_page(identification):
    driver = webdriver.Chrome(options=get_default_chrome_options())
    driver.maximize_window()

    try:
        driver.get(PAGE_URL)

        juditial_page = JuditialFunction(driver=driver)

        print("Ingresando datos...")
        juditial_page.enter_identification(identification=identification)
        # time.sleep(2)
        juditial_page.first_click_search_button()

        site_key = juditial_page.get_site_key()

        juditial_page.resolve_captcha_manual(site_key=site_key, page_url=PAGE_URL)

        # time.sleep(1)

        juditial_page.first_click_search_button()

        data_causes = juditial_page.get_data_causes()
        print("Data: ", json.dumps(data_causes, indent=4))
    
    except Exception as e:
        print(f"Ocurrió un error: {e}")

    # finally:
    #     driver.quit()

# init_juditial_funciton_page("BRIONES TUTIVEN DAVIS") 






