import requests
import time

TASK_TYPE = "ReCaptchaV3EnterpriseTaskProxyLess"

class CapSolverService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.capsolver.com"

    def create_task(self, website_url, website_key, page_action, task_type=TASK_TYPE):
        """
        Paso 1: Crea la tarea en CapSolver.
        Uso 'ProxyLess' si quieres que CapSolver use sus propios proxies, 
        o 'ReCaptchaV2Task' si vas a pasar el tuyo.
        """
        endpoint = f"{self.base_url}/createTask"
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": task_type,
                "websiteURL": website_url,
                "websiteKey": website_key,
                "pageAction": page_action,
                "minScore": 0.5 # Le pides a CapSolver un token de alta confianza
                # "proxy": "http:ip:port:user:pass" # Opcional si usas el tipo con proxy
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(endpoint, json=payload, headers=headers)
        result = response.json()

        if result.get("errorId") == 0:
            return result.get("taskId")
        else:
            print(f"Error al crear tarea: {result}")
            return None

    def get_task_result(self, task_id):
        """
        Paso 2: Consulta el estado de la tarea hasta que esté lista.
        """
        endpoint = f"{self.base_url}/getTaskResult"
        payload = {
            "clientKey": self.api_key,
            "taskId": task_id
        }

        while True:
            response = requests.post(endpoint, json=payload)
            result = response.json()
            print(result)

            if result.get("status") == "ready":
                print("✅ Captcha resuelto con éxito.")
                return result.get("solution").get("gRecaptchaResponse")
            
            if result.get("status") == "failed" or result.get("errorId") > 0:
                print(f"❌ Error en la resolución: {result}")
                return None
            
            print("⏳ Esperando resolución (5s)...")
            time.sleep(5)

# --- EJEMPLO DE USO ---
# API_KEY = "TU_API_KEY_AQUÍ"
# solver = CapSolverService(API_KEY)
# task_id = solver.create_task("https://www.google.com/recaptcha/api2/demo", "6Le-wvkSAAAAAPBMRTvw0Q4Muexq9bi0DJwx_mJ-")
# if task_id:
#     token = solver.get_task_result(task_id)
#     print(f"Token obtenido: {token}")