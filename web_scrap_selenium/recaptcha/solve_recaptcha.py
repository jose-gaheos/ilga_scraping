import os
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

api_key = os.getenv('API_KEY_2CAPTCHA')

solver = TwoCaptcha(apiKey=api_key)


def solve_recaptcha(site_key, page_url):
    try:
        print("api_key: ",api_key)
        response = solver.recaptcha(sitekey=site_key, url=page_url)
        print(f"Response: {response}")
        # print(f"Successfully solved the captcha. Captcha token {response}")
        return response.get('code')
    except Exception as e:
        print(f"Exception error: {e}")


def solve_image_captcha(image_base64):
    try:
        print("api_key", api_key)
        response = solver.normal(image_base64)

        return response.get('code')
    except Exception as e:
        print(f"Exception error in solve image captcha: {e}")

def solve_recaptcha_v3(site_key, page_url):
    try:
        print("api_key: ",api_key)
        response = solver.recaptcha(
            sitekey=site_key, 
            url=page_url, 
            version='v3', 
            enterprise=1, 
            # action='ruc_consulta',
            action='sri_consulta_publica_ruc',
            # action='ruc_consulta',
            score=0.9,
            # min_score = 0.7,
            # method = 'userrecaptcha'
        )
        print(f"Response: {response}")
        # print(f"Successfully solved the captcha. Captcha token {response}")
        return response.get('code')
    except Exception as e:
        print(f"Exception error: {e}")
        
