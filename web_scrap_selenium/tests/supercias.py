from selenium import webdriver
from pages.supercias_page import Supercias
from config import const
import json 

def init_supercias_bot(identification):
    supercias = Supercias("https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf")

    supercias.start_bot()

    supercias.enter_ruc_or_ci(identification=identification)
    
    image_base64 = supercias.get_image_captcha_base64_to_login(const.SUPERCIAS_IMAGE_CAPTCHA_LOGIN)
    code = supercias.resolve_captcha(image_base64)
    
    supercias.login(code)

    supercias.get_general_information()
    supercias.get_current_administrators_data()
    supercias.get_shareholder_data()
    supercias.get_annual_information()

    # print(supercias.data)

    print("Data: ", json.dumps(supercias.data, indent=4, ensure_ascii=False))

    # supercias.select_first_result()

# init_supercias_bot("0921839023001")
