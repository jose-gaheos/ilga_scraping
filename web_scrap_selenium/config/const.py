from selenium.webdriver.common.by import By


#SELECTORS FUNCION JUDICIAL
JF_URL = "https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros"
JF_RESULTS = '/causas'
JF_INPUT = (By.CSS_SELECTOR, "[formcontrolname='nombreDemandado']")
JF_SEARCH_BUTTON = (By.CSS_SELECTOR, "button[type='submit'][aria-label='Enviar formulario']")
JF_ACCORDION_CAUSES = (By.ID, "causas")
JF_PANELES_NAME = "mat-expansion-panel"
JF_PANEL_HEADER = "mat-expansion-panel-header"
JF_TITLE_CAUSE = ".//span[2]"
JF_CODE_CAUSE = ".//span[3]"

JF_LIST_CAUSES = (By.CLASS_NAME, "cuerpo")

JF_XPATH_GET_SITE_KEY = "//iframe[contains(@src, 'google.com/recaptcha/api2/anchor')]"


#SELECTORS SUPERCIAS
#LOGIN
SUPERCIAS_RADIO_RUC = "label[for='frmBusquedaCompanias:tipoBusqueda:1']" 
SUPERCIAS_INPUT_RUC = "frmBusquedaCompanias:parametroBusqueda_input"
SUPERCIAS_FIRST_RESULT_RUC = "//*[@id='frmBusquedaCompanias:parametroBusqueda_panel']/ul/li[1]"
SUPERCIAS_INPUT_CAPTCHA_LOGIN = "frmBusquedaCompanias:captcha"
SUPERCIAS_IMAGE_CAPTCHA_LOGIN = "frmBusquedaCompanias:captchaImage"
SUPERCIAS_BUTTON_SEARCH_LOGIN = "frmBusquedaCompanias:btnConsultarCompania"

#MENU
SUPERCIAS_URL_DOMAIN = "https://appscvsgen.supercias.gob.ec"
SUPERCIAS_MAIN_MENU = "frmMenu:menuPrincipal"
SUPERCIAS_ITEM_ACCIONISTAS = "frmMenu:menuAccionistas"
SUPERCIAS_TABLE_BODY_ACCIONISTAS = "frmInformacionCompanias:tblAccionistas_data"
SUPERCIAS_ROWS_ACCIONISTAS = "//tbody[@id='frmInformacionCompanias:tblAccionistas_data']"
SUPERCIAS_DIALOG_CAPTCHA = "#dlgCaptcha[hidden='false']"
SUPERCIAS_DIALOG_INPUT_CAPTCHA = "frmCaptcha:captcha"
SUPERCIAS_DIALOG_IMAGE_CAPTCHA = "frmCaptcha:captchaImage"
SUPERCIAS_DIALOG_VERIFY_CAPTCHA = "frmCaptcha:btnPresentarContenido"

SUPERCIAS_ACCORDION_GENERAL_INFORMATION = "//div[contains(@data-widget, 'frmInformacionCompanias')]"

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
TAG_ELEMENT_A = "a"


SUPERCIAS_KEY_CURRENT_ADMINISTRATORS = "Administradores actuales"
SUPERCIAS_KEY_GENERAL_INFORMATION = "General"
SUPERCIAS_KEY_SHAREHOLDERS = "Nómina accionistas"


SRI_XPATH_GET_SITE_KEY = "//iframe[contains(@src, 'recaptcha/enterprise/anchor')]"
SRI_ID_INPUT_SEARCH = "busquedaRucId"
SRI_XPATH_BUTTON_SEARCH = "//button[span[text()='Consultar']]"
SRI_ID_INPUT_USERNAME = "usuario"
SRI_ID_INPUT_PASSWORD = "password"

SRI_XPATH_BUTTON_LOGIN = "//input[@name='login']" 