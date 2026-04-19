import requests
from bs4 import BeautifulSoup
import os

# Configuración desde la "caja fuerte" de GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_TIENDA = "https://www.aostores.com/advanced_search"
ARCHIVO_MEMORIA = "vistos.txt"

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

def revisar_tienda():
    print("Revisando AO Stores...")
    try:
        # 1. Obtener la página
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        response = requests.get(URL_TIENDA, headers=headers, timeout=15)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Buscar productos (Ajustado a la estructura común de la tienda)
        # Nota: Si la tienda cambia su diseño, esto es lo que habría que actualizar.
        productos = soup.find_all('div', class_='product-item-info') 
        
        # 3. Leer productos ya vistos
        if os.path.exists(ARCHIVO_MEMORIA):
            with open(ARCHIVO_MEMORIA, "r") as f:
                vistos = set(f.read().splitlines())
        else:
            vistos = set()

        nuevos_encontrados = False

        for p in productos:
            try:
                # Extraer nombre y link
                enlace = p.find('a', class_='product-item-link')
                nombre = enlace.text.strip()
                link = enlace['href']
                
                # Si no lo hemos visto, mandamos alerta
                if nombre not in vistos:
                    mensaje = f"<b>🚨 ¡NUEVA OFERTA EN AO!</b>\n\n{nombre}\n\n<a href='{link}'>Ver producto aquí</a>"
                    enviar_mensaje(mensaje)
                    vistos.add(nombre)
                    nuevos_encontrados = True
            except:
                continue

        # 4. Guardar la memoria actualizada
        if nuevos_encontrados:
            with open(ARCHIVO_MEMORIA, "w") as f:
                f.write("\n".join(vistos))
            print("Se encontraron nuevos productos.")
        else:
            print("No hay nada nuevo por ahora.")
            
    except Exception as e:
        print(f"Error en el proceso: {e}")

if __name__ == "__main__":
    revisar_tienda()
