import csv
import os

def verify_images():
    """
    Verifica que las imágenes mencionadas en el CSV existan físicamente
    """
    # Verificar si existe el archivo
    if not os.path.exists('products.csv'):
        print("El archivo products.csv no existe.")
        return
    
    # Leer el archivo CSV
    images_in_csv = []
    with open('products.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'imagen_url' in row and row['imagen_url']:
                img_path = row['imagen_url']
                
                # Extraer nombre del archivo de la ruta
                if img_path.startswith('/static/fotos/'):
                    img_name = img_path.replace('/static/fotos/', '')
                elif img_path.startswith('static/fotos/'):
                    img_name = img_path.replace('static/fotos/', '')
                else:
                    img_name = os.path.basename(img_path)
                
                images_in_csv.append({
                    'sku': row['sku'],
                    'image_path': img_path,
                    'image_name': img_name
                })
    
    # Verificar qué imágenes existen físicamente
    img_dir = 'static/fotos'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
        print(f"Directorio creado: {img_dir}")
    
    files_in_dir = os.listdir(img_dir)
    
    print("\n=== Verificación de imágenes ===")
    print(f"Total de productos en CSV: {len(images_in_csv)}")
    print(f"Total de archivos en {img_dir}: {len(files_in_dir)}")
    print("\n--- Imágenes mencionadas en CSV ---")
    
    for img in images_in_csv:
        file_exists = img['image_name'] in files_in_dir
        status = "✓" if file_exists else "✗"
        print(f"{status} SKU {img['sku']}: {img['image_path']} ({img['image_name']})")
    
    print("\n--- Archivos en directorio ---")
    for file in files_in_dir:
        used = any(img['image_name'] == file for img in images_in_csv)
        status = "✓" if used else "?"
        print(f"{status} {file}")

if __name__ == "__main__":
    verify_images() 