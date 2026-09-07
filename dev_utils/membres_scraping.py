import os
import requests
from bs4 import BeautifulSoup

# 1. Definir URL y encabezados para simular un navegador
url = "https://kit-117.sorbonne-universite.fr/membres?page=13"
headers = {"User-Agent": "Mozilla/5.0"}

# Crear carpeta para guardar las imágenes si no existe
os.makedirs("fotos_miembros", exist_ok=True)

# 2. Descargar el contenido HTML
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Buscamos todas las tarjetas o bloques de información de miembros
    # En este sitio, los nombres están dentro de la etiqueta <h3>
    titulos = soup.find_all("h3")
    
    for h3 in titulos:
        # Extraer Nombre
        enlace_nombre = h3.find("a")
        if not enlace_nombre:
            continue
        nombre = enlace_nombre.text.strip()
        
        # El contenedor general de la persona suele estar unas etiquetas arriba del <h3>
        tarjeta = h3.find_parent("div").find_parent("div")
        
        # Extraer Cargo (está dentro del primer <p> junto al nombre)
        p_cargo = tarjeta.find("p")
        cargo = p_cargo.text.strip() if p_cargo else "Sin cargo indicado"
        
        # Extraer Correo
        a_mail = tarjeta.find("a", href=lambda h: h and h.startswith("mailto:"))
        email = a_mail["href"].replace("mailto:", "").strip() if a_mail else "Sin correo"
        
        # Extraer Imagen
        img = tarjeta.find("img")
        foto_url = None
        es_foto_real = False
        
        if img and img.get("src"):
            title_attr = img.get("title", "")
            # Si el title dice "Persona sans photo", es una foto por defecto/avatar
            if "sans photo" not in title_attr:
                foto_url = img["src"]
                # Asegurar que la URL sea absoluta
                if not foto_url.startswith("http"):
                    foto_url = "https://kit-117.sorbonne-universite.fr" + foto_url
                es_foto_real = True

        print(f"Nombre: {nombre}")
        print(f"Cargo: {cargo}")
        print(f"Email: {email}")
        print(f"Tiene foto real: {es_foto_real}")
        
        # 3. Descargar la foto si existe y es real
        if es_foto_real and foto_url:
            # Nombre limpio para guardar el archivo
            nombre_archivo = f"fotos_miembros/{nombre.replace(' ', '_')}.jpg"
            img_data = requests.get(foto_url, headers=headers).content
            
            with open(nombre_archivo, "wb") as f:
                f.write(img_data)
            print(f" -> Foto descargada: {nombre_archivo}")
            
        print("-" * 40)
else:
    print(f"Error al acceder a la página: status {response.status_code}")