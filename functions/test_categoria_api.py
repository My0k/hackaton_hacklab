import requests
import json
import csv
import base64
import os
from PIL import Image
import io

# Clave API (asegúrate de proteger esta clave en un entorno de producción)
API_KEY = "AIzaSyBCMRGWT57x1CSLeTJcCpy2mP-_4kJHZo8"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

def leer_categorias():
    """Lee las categorías del archivo materiales.csv"""
    categorias = []
    try:
        with open('materiales.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Saltar el encabezado
            for row in reader:
                if len(row) >= 2:
                    cats = row[1].split('|')
                    categorias.extend(cats)
        return list(set(categorias))  # Eliminar duplicados
    except Exception as e:
        print(f"Error al leer categorías: {e}")
        return []

def convertir_imagen_a_base64(ruta_imagen):
    """Convierte una imagen a base64 para enviarla a la API"""
    try:
        with open(ruta_imagen, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al convertir imagen: {e}")
        return None

def clasificar_con_gemini(descripcion=None, ruta_imagen=None):
    """Clasifica el material usando la API de Gemini"""
    categorias = leer_categorias()
    if not categorias:
        return "No se pudieron cargar las categorías"
    
    # Construir el prompt
    prompt = "Clasifica el siguiente material en UNA SOLA de estas categorías:\n"
    prompt += ", ".join(categorias) + "\n\n"
    
    if descripcion:
        prompt += f"Descripción: {descripcion}\n"
    
    prompt += "\nResponde ÚNICAMENTE con el nombre de la categoría que mejor coincida."
    
    # Preparar la solicitud
    parts = [{"text": prompt}]
    
    # Agregar imagen si está disponible
    if ruta_imagen:
        try:
            # Validar y optimizar la imagen
            img = Image.open(ruta_imagen)
            
            # Si es una imagen con transparencia (RGBA), convertirla a RGB
            if img.mode == 'RGBA':
                # Crear un fondo blanco y componer la imagen sobre él
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Usar el canal alfa como máscara
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Guardar en memoria
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG", quality=80)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_base64
                }
            })
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
            return "Error al procesar la imagen"
    
    # Configurar la solicitud
    payload = {
        "contents": [
            {
                "parts": parts
            }
        ]
    }
    
    # Realizar la solicitud
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Lanzar excepción si hay error HTTP
        
        resultado = response.json()
        
        # Extraer la respuesta
        if 'candidates' in resultado and len(resultado['candidates']) > 0:
            if 'content' in resultado['candidates'][0] and 'parts' in resultado['candidates'][0]['content']:
                return resultado['candidates'][0]['content']['parts'][0]['text'].strip()
        
        return "No se pudo obtener una respuesta clara"
    except Exception as e:
        print(f"Error en la solicitud: {e}")
        return f"Error en la solicitud: {str(e)}"

def main():
    print("Clasificación de Materiales con Gemini API")
    print("------------------------------------------")
    print("¿Qué tipo de entrada deseas proporcionar?")
    print("1) Texto/descripción")
    print("2) Imagen")
    print("3) Ambos (texto e imagen)")
    
    opcion = input("Selecciona una opción (1-3): ")
    
    descripcion = None
    ruta_imagen = None
    
    if opcion in ["1", "3"]:
        descripcion = input("Ingresa la descripción del material: ")
    
    if opcion in ["2", "3"]:
        ruta_imagen = input("Ingresa la ruta de la imagen: ")
        if not os.path.exists(ruta_imagen):
            print(f"La imagen en {ruta_imagen} no existe")
            return
    
    if not descripcion and not ruta_imagen:
        print("Debes proporcionar al menos una descripción o una imagen.")
        return
    
    print("\nClasificando material...")
    resultado = clasificar_con_gemini(descripcion, ruta_imagen)
    
    print("\nResultado de la clasificación:")
    print(resultado)

if __name__ == "__main__":
    main()
