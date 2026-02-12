import requests
import base64
import time 
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def download_image_to_base64(url_image):
    try:
        response = requests.get(url_image, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 3. Convertir los bytes de la imagen a Base64
            # Esto elimina el error de formato porque enviamos el contenido puro
            img_base64 = base64.b64encode(response.content).decode('utf-8')
            return img_base64        
            
        else:
            print(f"No se pudo descargar la imagen. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def write_like_as_human(elemento, texto):
    for caracter in texto:
        elemento.send_keys(caracter)
        # Pausa aleatoria entre teclas entre 0.05 y 0.2 segundos
        time.sleep(random.uniform(0.5, 1))

def escribir_con_error_humano(elemento, texto):
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
    for _ in range(3):
        elemento.send_keys(Keys.BACKSPACE)
        time.sleep(random.uniform(0.5, 0.7))
    
    # 4. RE-ESCRIBIR los últimos 3 caracteres
    ultimos_tres = texto[-3:]
    for caracter in ultimos_tres:
        elemento.send_keys(caracter)
        time.sleep(random.uniform(0.5, 0.8))
        
    # 5. Salir del campo (Tab para confirmar el cambio, muy humano)
    elemento.send_keys(Keys.TAB)
    time.sleep(random.uniform(0.5, 1.0))