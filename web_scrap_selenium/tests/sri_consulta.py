from selenium import webdriver
from pages.sri_page import SRI
from config import const
import json 
import time

PAGE_URL_CONSULTA_RUC = "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc"
PAGE_URL = "https://srienlinea.sri.gob.ec/sri-en-linea/contribuyente/perfil"
def init_sri_bot(identification):

    sri = SRI(url=PAGE_URL)
    
    sri.start_bot()
    sri.login()
    time.sleep(2)
    sri.redirect_to_request_ruc(url=PAGE_URL_CONSULTA_RUC)
    time.sleep(2)
    if sri.enter_ruc_or_ci(identification=identification):
        sri.show_establishments()
        time.sleep(2)
        sri.print_screen()
    else:
        print("No se encontro el detalle de información")


# init_supercias_bot("0921839023001")
