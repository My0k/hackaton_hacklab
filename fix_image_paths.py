import csv
import os

def fix_image_paths():
    """
    Corrige las rutas de las imágenes en products.csv para asegurar consistencia.
    """
    # Verificar si existe el archivo
    if not os.path.exists('products.csv'):
        print("El archivo products.csv no existe.")
        return
    
    # Leer el archivo actual
    rows = []
    with open('products.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            # Corregir la ruta de imagen
            if 'imagen_url' in row:
                img_path = row['imagen_url']
                
                # Quitar /static/ o static/ del inicio si existe
                if img_path.startswith('/static/fotos/'):
                    img_path = img_path[13:]  # Quitar '/static/fotos/'
                elif img_path.startswith('static/fotos/'):
                    img_path = img_path[12:]  # Quitar 'static/fotos/'
                elif img_path.startswith('/static/'):
                    img_path = img_path[8:]   # Quitar '/static/'
                elif img_path.startswith('static/'):
                    img_path = img_path[7:]   # Quitar 'static/'
                
                # Guardar solo el nombre del archivo
                row['imagen_url'] = img_path
            
            rows.append(row)
    
    # Escribir el archivo corregido
    with open('products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Se corrigieron las rutas de imágenes en {len(rows)} productos.")

if __name__ == "__main__":
    fix_image_paths() 