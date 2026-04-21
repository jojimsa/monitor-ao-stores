import requests
import os

# Configuración
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
# URL de la API interna que alimenta la página de Advanced Search
URL_API = "https://www.aostores.com/rest/V1/search?searchCriteria[requestName]=advanced_search_container&searchCriteria[filterGroups][0][filters][0][field]=category_id&searchCriteria[filterGroups][0][filters][0][value]=2"
ARCHIVO_MEMORIA = "vistos.txt"

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando a Telegram: {e}")

def revisar_tienda():
    try:
        # Consultamos directamente la fuente de datos
        headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json'}
        response = requests.get(URL_API, headers=headers, timeout=20)
        datos = response.json()
        
        # Extraemos los productos del JSON de respuesta
        items = datos.get('items', [])
        print(f"Productos detectados: {len(items)}")
        
        if os.path.exists(ARCHIVO_MEMORIA):
            with open(ARCHIVO_MEMORIA, "r") as f:
                vistos = set(f.read().splitlines())
        else:
            vistos = set()

        nuevos_encontrados = False
        for item in items:
            # En el JSON de esta tienda, el ID o la URL están en los atributos
            sku = item.get('sku')
            # Construimos la URL basada en el SKU para que el usuario pueda hacer clic
            link = f"https://www.aostores.com/catalogsearch/result/?q={sku}"
            
            if sku and sku not in vistos:
                mensaje = f"<b>🚨 NUEVA OFERTA</b>\nSKU: {sku}\n<a href='{link}'>Ver resultado de búsqueda</a>"
                enviar_mensaje(mensaje)
                vistos.add(sku)
                nuevos_encontrados = True

        if nuevos_encontrados:
            with open(ARCHIVO_MEMORIA, "w") as f:
                f.write("\n".join(vistos))
            print("Novedades procesadas.")
        else:
            print("Sin productos nuevos.")

    except Exception as e:
        print(f"Error en la revisión: {e}")

if __name__ == "__main__":
    revisar_tienda()
