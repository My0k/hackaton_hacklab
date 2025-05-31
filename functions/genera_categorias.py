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

def procesar_imagen(imagen_archivo):
    """Procesa una imagen para enviarla a la API"""
    try:
        # Abrir y optimizar la imagen
        img = Image.open(imagen_archivo)
        
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
        
        return img_base64
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None

def generar_categorias(descripcion, imagen_archivo=None):
    """Genera categorías para el material usando la API de Gemini"""
    categorias = leer_categorias()
    if not categorias:
        return "No se pudieron cargar las categorías"
    
    # Construir el prompt
    prompt = "Clasifica el siguiente material en UNA O MÁS de estas categorías:\n"
    prompt += ", ".join(categorias) + "\n\n"
    
    if descripcion:
        prompt += f"Descripción: {descripcion}\n"
    
    prompt += "\nResponde ÚNICAMENTE con los nombres de las categorías que mejor coincidan, separados por comas (máximo 3 categorías)."
    
    # Preparar la solicitud
    parts = [{"text": prompt}]
    
    # Agregar imagen si está disponible
    if imagen_archivo:
        try:
            img_base64 = procesar_imagen(imagen_archivo)
            if img_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_base64
                    }
                })
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
    
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

def generar_descripcion_larga(descripcion_corta, imagen_archivo=None):
    """Genera una descripción larga y detallada para el material usando la API de Gemini"""
    
    # Construir el prompt
    prompt = """Genera una descripción breve y técnica para un material reciclable basada en la siguiente información. 
    La descripción debe ser concisa (máximo 4 líneas) y enfocarse en:
    - Que se muestra en la imagen
    - Cuanto material se puede reciclar o reutilizar
    - Cantidad estimada o dimensiones aproximadas
    - Potencial de reciclaje o reutilización
    
    Descripción breve: """ + descripcion_corta
    
    prompt += "\n\nResponde con un texto conciso y directo, enfocado en datos técnicos más que en lenguaje promocional."
    
    # Preparar la solicitud
    parts = [{"text": prompt}]
    
    # Agregar imagen si está disponible
    if imagen_archivo:
        try:
            img_base64 = procesar_imagen(imagen_archivo)
            if img_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_base64
                    }
                })
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
    
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
        
        return "No se pudo generar una descripción detallada."
    except Exception as e:
        print(f"Error en la solicitud: {e}")
        return f"Error en la solicitud: {str(e)}"

def generar_titulo(descripcion, imagen_archivo=None):
    """Genera un título atractivo para el material usando la API de Gemini"""
    
    # Construir el prompt
    prompt = """Genera un título corto y atractivo para un producto de segunda mano basado en la siguiente descripción.
    El título debe ser conciso (máximo 6 palabras) y descriptivo, adecuado para un marketplace de materiales reciclables.
    
    Descripción: """ + descripcion
    
    prompt += "\n\nResponde ÚNICAMENTE con el título, sin comillas ni puntuación adicional."
    
    # Preparar la solicitud
    parts = [{"text": prompt}]
    
    # Agregar imagen si está disponible
    if imagen_archivo:
        try:
            img_base64 = procesar_imagen(imagen_archivo)
            if img_base64:
                parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_base64
                    }
                })
        except Exception as e:
            print(f"Error al procesar la imagen: {e}")
    
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
        
        return "Material Reciclable"
    except Exception as e:
        print(f"Error en la solicitud: {e}")
        return "Material Reciclable"
