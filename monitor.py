import requests
from bs4 import BeautifulSoup
import os

# Configuración
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
    print("Iniciando revisión de AO Stores...")
    try:
        # Headers más completos para parecer un navegador real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(URL_TIENDA, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Intentamos capturar los productos con selectores más comunes en Magento (el sistema de esa tienda)
        productos = soup.select('.product-item') or soup.select('.product-item-info')
        
        print(f"Productos detectados en la página: {len(productos)}")
        
        if os.path.exists(ARCHIVO_MEMORIA):
            with open(ARCHIVO_MEMORIA, "r") as f:
                vistos = set(f.read().splitlines())
        else:
            vistos = set()

        nuevos_encontrados = False

        for p in productos:
            try:
                # Intentamos obtener el link y el nombre de forma más robusta
                enlace_tag = p.find('a', class_='product-item-link') or p.find('a')
                if not enlace_tag: continue
                
                nombre = enlace_tag.get_text().strip()
                link = enlace_tag['href']
                
                if nombre and nombre not in vistos:
                    mensaje = f"<b>🚨 ¡NUEVA OFERTA EN AO!</b>\n\n{nombre}\n\n<a href='{link}'>Ver producto aquí</a>"
                    enviar_mensaje(mensaje)
                    vistos.add(nombre)
                    nuevos_encontrados = True
            except Exception as e:
                print(f"Error procesando un producto: {e}")
                continue

        if nuevos_encontrados:
            with open(ARCHIVO_MEMORIA, "w") as f:
                f.write("\n".join(vistos))
            print("Se enviaron nuevas alertas.")
        else:
            print("No se encontraron productos nuevos en esta vuelta.")
            
    except Exception as e:
        print(f"Error crítico en el proceso: {e}")

if __name__ == "__main__":
    revisar_tienda()
