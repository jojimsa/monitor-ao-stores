import requests
from bs4 import BeautifulSoup
import os
import re

# Configuración
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# VOLVEMOS A TU URL ORIGINAL
URL_TIENDA = "https://www.aostores.com/advanced_search"
ARCHIVO_MEMORIA = "vistos.txt"

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def revisar_tienda():
    print(f"Revisando URL original: {URL_TIENDA}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(URL_TIENDA, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # MÉTODO NUEVO: Buscamos todos los enlaces que tengan la estructura de un producto de AO
        # Usualmente los productos en esta tienda tienen '/producto/' en el link o clases específicas
        enlaces_productos = soup.find_all('a', href=re.compile(r'/producto/|/p/'))
        
        # Si el método anterior falla, intentamos con el selector de items
        if not enlaces_productos:
            enlaces_productos = soup.select('.product-item-link') or soup.select('.product-item a')

        print(f"Productos detectados: {len(enlaces_productos)}")
        
        if os.path.exists(ARCHIVO_MEMORIA):
            with open(ARCHIVO_MEMORIA, "r") as f:
                vistos = set(f.read().splitlines())
        else:
            vistos = set()

        nuevos_encontrados = False

        for link_tag in enlaces_productos:
            link = link_tag.get('href')
            nombre = link_tag.get_text().strip()
            
            # Limpiamos el nombre porque a veces traen espacios extraños
            if not nombre:
                nombre = link.split('/')[-1].replace('.html', '').replace('-', ' ')

            if link and link not in vistos:
                mensaje = f"<b>🚨 NUEVA OFERTA (Advanced Search)</b>\n\n{nombre.upper()}\n\n<a href='{link}'>Ver producto aquí</a>"
                enviar_mensaje(mensaje)
                vistos.add(link) # Guardamos el link que es único
                nuevos_encontrados = True

        if nuevos_encontrados:
            with open(ARCHIVO_MEMORIA, "w") as f:
                f.write("\n".join(vistos))
            print("Novedades enviadas a Telegram.")
        else:
            print("No se detectaron cambios en los productos.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    revisar_tienda()
