#######################################################################################
#
#    GAHEOS S.A.
#    Copyright (C) 2020-TODAY GAHEOS S.A. (https://www.gaheos.com)
#    Author: Leonardo Gavidia Guerra | @leogavidia
#
#    See LICENSE file for full copyright and licensing details.
#
#######################################################################################
# from odoo.tools.zeep.client import TIMEOUT

# Await
AWAIT_MOVE = 0.3
AWAIT_CLICK = 0.3
AWAIT_KEYS = 0.2
AWAIT_OPEN = 2.5
AWAIT_LOCATE = 20.0
AWAIT_LOCATE_SHORT = 5.0
AWAIT_DOWNLOAD = 0.2
AWAIT_MEDIUM = 1.0
AWAIT_SHORT = 0.5

# Retry
RETRY_TIMES_MAXIMUM = 200
RETRY_TIMES_LONG = 30
RETRY_TIMES_MEDIUM = 10
RETRY_TIMES_SHORT = 5
RETRY_TIMES_MINIMUM = 3

# Timeout
TIMEOUT_MAXIMUM = 200
TIMEOUT_LONG = 60
TIMEOUT_MEDIUM = 30
TIMEOUT_SHORT = 10
TIMEOUT_MINIMUM = 5

# States
STATE_INITIAL = 'INITIAL'
STATE_PENDING = 'PENDING'
STATE_READY = 'READY'
STATE_EMPTY = 'EMPTY'
STATE_SUCCESS = 'SUCCESS'
STATE_INVALID = 'INVALID'
STATE_CLOSED = 'CLOSED'
STATE_ERROR = 'ERROR'
STATE_FAILED = 'FAILED'
STATE_PAGE_ERROR = 'PAGE_ERROR'
STATE_DATA_EXTRACTION = 'DATA_EXTRACTION'
# Actions
ACTION_SETTINGS = 'SETTINGS'
ACTION_HOME = 'HOME'
ACTION_LOGIN = 'LOGIN'
ACTION_USER = 'USER'
ACTION_DOCUMENTS_A0 = 'DOCUMENTS_A0'
ACTION_DOCUMENTS_A1 = 'DOCUMENTS_A1'
ACTION_DOCUMENTS = 'DOCUMENTS'
ACTION_DOCUMENTS_RECAPTCHA = 'DOCUMENTS_FORM_RECAPTCHA'
ACTION_DOCUMENTS_TABLE = 'DOCUMENTS_TABLE'

ACTION_HOME_SUPERCIAS = 'HOME_SUPERCIAS'

ACTION_SUPERCIA_SEARCH = 'SEARCH_SUPERCIAS'
ACTION_SUPERCIA_RECAPTCHA = 'SUPERCIA_RECAPTCHA'
ACTION_RECAPTCHA = 'RECAPTCHA'
# Home Action
HOME_URL = 'https://srienlinea.sri.gob.ec/sri-en-linea/inicio/NAT'
HOME_XPATH_TEST = "//a[@href='/sri-en-linea/inicio/NAT']"

# Login Action
LOGIN_XPATH_LINK = "//a[contains(@class, 'sri-tamano-link-iniciar-sesion')]"
LOGIN_XPATH_USERNAME_INPUT = "//input[@id='usuario']"
LOGIN_XPATH_PASSWORD_INPUT = "//input[@id='password']"
LOGIN_XPATH_CI_INPUT = "//input[@id='ciAdicional']"
LOGIN_XPATH_BUTTON = "//input[@id='kc-login']"
LOGIN_XPATH_TEST = [
    "//label[contains(@class, 'nombre-contribuyente')]",
    "//label[contains(@class, 'nombre-usuario')]",
    "//a[@href='/sri-en-linea/SriClaves/Generacion/internet/actualizar']"
]

# User Action
USER_XPATH_LINK = "//a[@href='/sri-en-linea/inicio/NAT']"
USER_XPATH_MODAL = "mat-dialog-0"
USER_XPATH_MODAL_BUTTON = ".//button[contains(@class, 'eliminar-boton')]"

# Documents Action
DOCUMENTS_URL = 'https://srienlinea.sri.gob.ec/tuportal-internet/accederAplicacion.jspa?redireccion=57&idGrupo=55'
DOCUMENTS_XPATH_MODAL = "mat-dialog-0"
DOCUMENTS_XPATH_BUTTON_COLLAPSE = "//button[@title='Facturación Electrónica']"
DOCUMENTS_XPATH_BUTTON_ACTION = "//a/span[text()='Comprobantes electrónicos recibidos']"
DOCUMENTS_XPATH_TEST = "//input[@id='frmPrincipal:txtParametro']"

# Documents Form Action
DOCUMENTS_FORM_XPATH_YEAR = "//select[@id='frmPrincipal:ano']"
DOCUMENTS_FORM_XPATH_MONTH = "//select[@id='frmPrincipal:mes']"
DOCUMENTS_FORM_XPATH_DAY = "//select[@id='frmPrincipal:dia']"
DOCUMENTS_FORM_XPATH_DOCUMENT_TYPE = "//select[@id='frmPrincipal:cmbTipoComprobante']"
DOCUMENTS_FORM_XPATH_TABLE = "frmPrincipal:tablaCompRecibidos"
DOCUMENTS_FORM_XPATH_WARNING = '//span[contains(@class, "ui-messages-warn-summary")]'
DOCUMENTS_FORM_XPATH_WARNING_MSG = 'No existen datos'

# Documents Download Action
DOCUMENTS_TABLE_XPATH_DATA = "frmPrincipal:tablaCompRecibidos_data"
DOCUMENTS_TABLE_XPATH_ROW = ".//tr[@data-ri]"
DOCUMENTS_TABLE_XPATH_ROW_INDEX = ".//tr[@data-ri='%s']"
DOCUMENTS_TABLE_XPATH_PAGES = '//span[contains(@class, "ui-paginator-current")]'
DOCUMENTS_TABLE_XPATH_PREV_PAGE = "//span[contains(@class, 'ui-paginator-prev')]"
DOCUMENTS_TABLE_XPATH_NEXT_PAGE = "//span[contains(@class, 'ui-paginator-next')]"
DOCUMENTS_TABLE_XPATH_LAST_PAGE = "//span[contains(@class, 'ui-paginator-last')]"

# Documents Form Recaptcha Action
DOCUMENTS_RECAPTCHA_XPATH_CONTAINER = "g-recaptcha"
DOCUMENTS_RECAPTCHA_XPATH_ATTRIBUTE = "data-sitekey"
DOCUMENTS_RECAPTCHA_XPATH_RESPONSE = "g-recaptcha-response"

DOCUMENT_TYPES = ['1', '2', '3', '4', '6']
DOCUMENTS_DOWNLOAD_URL = 'https://srienlinea.sri.gob.ec/comprobantes-electronicos-internet/pages/consultas/recibidos/comprobantesRecibidos.jsf'
DOCUMENTS_DOWNLOAD_PARAM_XML = 'frmPrincipal:tablaCompRecibidos:%s:lnkXml'
DOCUMENTS_DOWNLOAD_PARAM_PDF = 'frmPrincipal:tablaCompRecibidos:%s:lnkPdf'
DOCUMENTS_DOWNLOAD_PARAM = {
    'xml': DOCUMENTS_DOWNLOAD_PARAM_XML,
    'pdf': DOCUMENTS_DOWNLOAD_PARAM_PDF
}
DOCUMENTS_DOWNLOAD_HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua-mobile': '?0',
}

SUPERCIAS_XPATH_SEARCH_FORM = '//*[@id="frmBusquedaCompanias:panelParametrosBusqueda"]'

#SELECTORS SUPERCIAS
#LOGIN
SUPERCIAS_XPATH_RADIO_RUC = "label[for='frmBusquedaCompanias:tipoBusqueda:1']" 
SUPERCIAS_INPUT_RUC = "frmBusquedaCompanias:parametroBusqueda_input"
SUPERCIAS_XPATH_FIRST_RESULT_RUC = "//*[@id='frmBusquedaCompanias:parametroBusqueda_panel']/ul/li[1]"
SUPERCIAS_INPUT_CAPTCHA_LOGIN = "frmBusquedaCompanias:captcha"
SUPERCIAS_IMAGE_CAPTCHA_LOGIN = "frmBusquedaCompanias:captchaImage"
SUPERCIAS_BUTTON_SEARCH_LOGIN = "frmBusquedaCompanias:btnConsultarCompania"

#MENU
SUPERCIAS_URL_DOMAIN = "https://appscvsgen.supercias.gob.ec"
SUPERCIAS_MAIN_MENU = "frmMenu:menuPrincipal"
SUPERCIAS_ITEM_ACCIONISTAS = "frmMenu:menuAccionistas"
SUPERCIAS_TABLE_BODY_ACCIONISTAS = "frmInformacionCompanias:tblAccionistas_data"
SUPERCIAS_ROWS_ACCIONISTAS = "//tbody[@id='frmInformacionCompanias:tblAccionistas_data']"
SUPERCIAS_DIALOG_CAPTCHA = "    "
SUPERCIAS_DIALOG_INPUT_CAPTCHA = "frmCaptcha:captcha"
#SUPERCIAS_DIALOG_IMAGE_CAPTCHA = "frmCaptcha:captchaImage"
SUPERCIAS_DIALOG_IMAGE_CAPTCHA = "//*[@id='frmCaptcha:captchaImage']"
SUPERCIAS_DIALOG_VERIFY_CAPTCHA = "frmCaptcha:btnPresentarContenido"

SUPERCIAS_ACCORDION_GENERAL_INFORMATION = "//div[contains(@data-widget, 'frmInformacionCompanias')]"
SUPERCIAS_PARENT_ACCORDION_GENERAL_INFORMATION = "//span[@id='frmInformacionCompanias:panelGroupInformacionCompanias']//div[contains(@class, 'ui-accordion')]"

SUPERCIAS_XPATH_ACCORDION_INFORMATION_ITEM = "./div"
SUPERCIAS_CLASS_UI_ACCORDION_HEADER = "ui-accordion-header"

SUPERCIAS_CLASS_UI_ACCORDION_CONTENT = "ui-accordion-content"

SUPERCIAS_XPATH_ROWS_TBODY_CONTENT = "./table/tbody/tr"

SUPERCIAS_CLASS_ROW_ITEM_CONTENT_FIRST_COLUMN = "columna1"

SUPERCIAS_XPATH_CELL_VALUE_ITEM = "./following-sibling::td"

SUPERCIAS_SELECTOR_CELL_VALUE_INPUT = "input, textarea"

SUPERCIAS_XPATH_HEADER_ACCORDION_ITEM = ".//div/span"

SUPERCIAS_ITEM_CURRENT_ADMINISTRATORS = "frmMenu:menuAdministradoresActuales"
SUPERCIAS_TABLE_BODY_CURRENT_ADMINISTRATORS = "frmInformacionCompanias:tblAdministradoresActuales_data"
SUPERCIAS_ROWS_CURRENT_ADMINISTRATORS = "//tbody[@id='frmInformacionCompanias:tblAdministradoresActuales_data']/tr"
SUPERCIAS_HEADER_CURRENT_ADMINISTRATORS = "//thead[@id='frmInformacionCompanias:tblAdministradoresActuales_head']/tr/th"
SUPERCIAS_PANEL_PDF_OBJECT = "#panelInternoPresentarDocumentoPdf_content object"
SUPERCIAS_PDF_BUTTON_CLOSE = "//span[@id='dlgPresentarDocumentoPdf_title']/following-sibling::a"
SUPERCIAS_PDF_UI_WIDGET_OVERLAY = "ui-widget-overlay"
SUPERCIAS_XPATH_BUTTON_SIGN = "//div[@id='dlgPresentarDocumentoPdfConFirmasElectronicas']//button[contains(., 'Aceptar')]"
SUPERCIAS_CSS_SELECTOR_DIALOG_CAPTCHA_DISPLAY = "div#dlgCaptcha[style*='display: block']"

SUPERCIAS_ITEM_ANNUAL_INFORMATION = "frmMenu:menuInformacionAnualPresentada"
SUPERCIAS_CONTAINER_TABLE_ANNUAL_INFORMATION = "frmInformacionCompanias:panelGroupInformacionCompanias"
SUPERCIAS_TABLE_HEADER_ANNUAL_INFORMATION = "frmInformacionCompanias:tblInformacionAnual_head"
SUPERCIAS_XPATH_HEADER_TITLE_ANNUAL_INFORMATION = "//thead[@id='frmInformacionCompanias:tblInformacionAnual_head']/tr/th"
SUPERCIAS_XPATH_INPUT_NUMBER_DOCUMENT = "//thead[@id='frmInformacionCompanias:tblInformacionAnual_head']/tr/th[3]//input"
SUPERCIAS_ROWS_ANNUAL_INFORMATION = "//tbody[@id='frmInformacionCompanias:tblInformacionAnual_data']/tr"

TAG_ELEMENT_TD = "td"
TAG_ELEMENT_TH = "th"
TAG_ELEMENT_A = "a"
TAG_ELEMENT_TABLE = "table"

SUPERCIAS_KEY_CURRENT_ADMINISTRATORS = "Administradores actuales"
SUPERCIAS_KEY_GENERAL_INFORMATION = "General"
SUPERCIAS_KEY_SHAREHOLDERS = "Nómina accionistas"




#SELECTORS FUNCION JUDICIAL
JF_URL = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"
JF_RESULTS = '/causas'
JF_SELECTOR_INPUT = "[formcontrolname='nombreDemandado']"
JF_SELECTOR_SEARCH_BUTTON =  "button[type='submit'][aria-label='Enviar formulario']"
JF_ACCORDION_CAUSES =  "causas"
JF_CLASS_LIST_CAUSES = "causa-individual"
JF_PANELES_NAME = "mat-expansion-panel"
JF_PANEL_HEADER = "mat-expansion-panel-header"
JF_TITLE_CAUSE = ".//span[2]"
JF_CODE_CAUSE = ".//span[3]"

JF_LIST_CAUSES =  "cuerpo"

JF_XPATH_GET_SITE_KEY = "//iframe[contains(@src, 'google.com/recaptcha/api2/anchor')]"


#SRI SELECTORS
SRI_XPATH_GET_SITE_KEY = "//iframe[contains(@src, 'recaptcha/enterprise/anchor')]"
SRI_ID_INPUT_SEARCH = "busquedaRucId"
# SRI_XPATH_BUTTON_SEARCH = "//button[span[text()='Consultar']]"
SRI_XPATH_BUTTON_SEARCH = "//button[contains(@class, 'ui-button') and not(@disabled)]//span[text()='Consultar']"
SRI_ID_INPUT_USERNAME = "usuario"
SRI_ID_INPUT_PASSWORD = "password"

SRI_XPATH_BUTTON_LOGIN = "//input[@name='login']" 
SRI_TAG_PROFILE = "perfil-contribuyente"

SRI_ID_MENU = "mySidebar2"
SRI_ID_BUTTON_MENU = "sri-menu"
SRI_XPATH_MENU_ITEM_RUC = "//*[@id='mySidebar']/p-panelmenu/div/div[2]/div[1]"
SRI_XPATH_MENU_ITEM_CONSULTA = "//*[@id='mySidebar']/p-panelmenu/div/div[2]/div[2]/div/p-panelmenusub/ul/li[1]/a"
SRI_XPATH_MORE_STABLISHMENTS = "//button[.//span[contains(., 'Mostrar establecimientos')]]"

SRI_CLASS_LABEL_BOLD = "sri-bold"
SRI_XPATH_DIV_VALUE = "./ancestor::div[1]/following-sibling::div"
SRI_XPATH_LEGAL_NAME = "./following-sibling::div[1]"

SRI_XPATH_TITLE_MAIN = "//th[contains(text(), 'Actividad económica principal')]"

SRI_XPATH_ACTIVITY_MAIN = f"{SRI_XPATH_TITLE_MAIN}/ancestor::div[contains(@class, 'col-sm-6')]/following-sibling::div//td"
SRI_CLASS_ALL_VALUES = "tamano-defecto-campos"

CONSULTA_RUC_SRI_URL = "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc"
CONSULTA_SUPERCIAS_URL = "https://appscvsgen.supercias.gob.ec/consultaCompanias/societario/busquedaCompanias.jsf"
CONSULTA_FUNCION_JUDICIAL_URL = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"

#