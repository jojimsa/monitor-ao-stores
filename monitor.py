import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

# Configuración
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_TIENDA = "https://www.aostores.com/advanced_search"
ARCHIVO_MEMORIA = "vistos.txt"

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def revisar_tienda():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(URL_TIENDA)
        
        # Espera hasta 20 segundos a que aparezca al menos un producto
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-item")))
        
        # Extraer los productos una vez cargados
        items = driver.find_elements(By.CLASS_NAME, "product-item")
        print(f"Productos detectados: {len(items)}")
        
        if os.path.exists(ARCHIVO_MEMORIA):
            with open(ARCHIVO_MEMORIA, "r") as f:
                vistos = set(f.read().splitlines())
        else:
            vistos = set()

        nuevos = False
        for item in items:
            try:
                link_tag = item.find_element(By.CLASS_NAME, "product-item-link")
                nombre = link_tag.text.strip()
                link = link_tag.get_attribute("href")
                
                if link not in vistos:
                    enviar_mensaje(f"<b>🚨 NUEVA OFERTA</b>\n\n{nombre}\n\n<a href='{link}'>Ver producto</a>")
                    vistos.add(link)
                    nuevos = True
            except:
                continue

        if nuevos:
            with open(ARCHIVO_MEMORIA, "w") as f:
                f.write("\n".join(vistos))

    except Exception as e:
        print(f"Error: No se cargaron los productos en el tiempo esperado. {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    revisar_tienda()
