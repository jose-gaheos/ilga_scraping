import time
import random
from selenium.webdriver.common.keys import Keys

def escribir_con_error_humano(elemento, texto, error_delete = -3):
    # 1. Hacer FOCUS (Clic en el elemento)
    elemento.click()
    time.sleep(random.uniform(0.5, 1))
    
    # Escribir el texto completo inicialmente
    for caracter in texto:
        elemento.send_keys(caracter)
        time.sleep(random.uniform(0.5, 1.5))
    
    # 2. Simular "Duda" o "Error" (Pausa antes de borrar)
    time.sleep(random.uniform(1, 2))
    
    # 3. ELIMINAR los últimos 3 caracteres uno a uno
    for _ in range(abs(error_delete)):
        elemento.send_keys(Keys.BACKSPACE)
        time.sleep(random.uniform(0.5, 0.7))
    
    # 4. RE-ESCRIBIR los últimos 3 caracteres
    ultimos_tres = texto[error_delete:]
    for caracter in ultimos_tres:
        elemento.send_keys(caracter)
        time.sleep(random.uniform(0.5, 0.8))
        
    # 5. Salir del campo (Tab para confirmar el cambio, muy humano)
    elemento.send_keys(Keys.TAB)
    time.sleep(random.uniform(0.5, 1.0))